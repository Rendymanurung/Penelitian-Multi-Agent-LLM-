from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass
from typing import Any

from .config import ProviderConfig


@dataclass
class ModelResponse:
    provider: str
    model: str
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _call_openai(config: ProviderConfig, system_prompt: str, user_prompt: str) -> tuple[str, int, int]:
    from openai import OpenAI

    client = OpenAI(api_key=config.api_key)
    response = client.responses.create(
        model=config.model,
        instructions=system_prompt,
        input=user_prompt,
        max_output_tokens=1400,
    )
    usage = getattr(response, "usage", None)
    return (
        getattr(response, "output_text", "") or "",
        int(getattr(usage, "input_tokens", 0) or 0),
        int(getattr(usage, "output_tokens", 0) or 0),
    )


def _call_gemini(config: ProviderConfig, system_prompt: str, user_prompt: str) -> tuple[str, int, int]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=config.api_key)
    response = client.models.generate_content(
        model=config.model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
            response_mime_type="application/json",
        ),
    )
    usage = getattr(response, "usage_metadata", None)
    return (
        getattr(response, "text", "") or "",
        int(getattr(usage, "prompt_token_count", 0) or 0),
        int(getattr(usage, "candidates_token_count", 0) or 0),
    )


def _call_groq(config: ProviderConfig, system_prompt: str, user_prompt: str) -> tuple[str, int, int]:
    from groq import Groq

    client = Groq(api_key=config.api_key)
    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_completion_tokens=1400,
        response_format={"type": "json_object"},
    )
    usage = getattr(response, "usage", None)
    content = response.choices[0].message.content or ""
    return (
        content,
        int(getattr(usage, "prompt_tokens", 0) or 0),
        int(getattr(usage, "completion_tokens", 0) or 0),
    )


def call_provider(config: ProviderConfig, system_prompt: str, user_prompt: str) -> ModelResponse:
    started = time.perf_counter()
    if config.name == "openai":
        text, input_tokens, output_tokens = _call_openai(config, system_prompt, user_prompt)
    elif config.name == "gemini":
        text, input_tokens, output_tokens = _call_gemini(config, system_prompt, user_prompt)
    elif config.name == "groq":
        text, input_tokens, output_tokens = _call_groq(config, system_prompt, user_prompt)
    else:
        raise ValueError(f"Unsupported provider: {config.name}")

    return ModelResponse(
        provider=config.name,
        model=config.model,
        text=text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_seconds=round(time.perf_counter() - started, 4),
    )


def parse_json_response(text: str) -> dict[str, Any]:
    """Parse strict JSON, tolerating surrounding Markdown fences."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError(f"Model did not return JSON: {cleaned[:300]}")
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Model JSON response must be an object")
    verdict = str(data.get("verdict", "")).upper().strip()
    if verdict not in {"CORRECT", "BUGGY", "UNCERTAIN"}:
        raise ValueError(f"Invalid verdict: {verdict!r}")
    data["verdict"] = verdict
    data.setdefault("reason", "")
    data.setdefault("bug_location", "")
    data.setdefault("suggested_fix", "")
    return data
