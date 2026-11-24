from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from .config import ProviderConfig
from .providers import call_provider, parse_json_response

SYSTEM_PROMPT = """You are a careful Python requirement-conformance reviewer.
Classify whether the supplied implementation satisfies the natural-language requirement.
Return exactly one JSON object with these keys:
{
  \"verdict\": \"CORRECT\" | \"BUGGY\" | \"UNCERTAIN\",
  \"reason\": \"brief explanation grounded in the requirement and code\",
  \"bug_location\": \"file/function/line or empty string\",
  \"suggested_fix\": \"complete replacement implementation or empty string\"
}
Do not invent requirements. Do not label style preferences as functional bugs. If evidence is insufficient, use UNCERTAIN.
If verdict is CORRECT, suggested_fix must be an empty string.
"""


def make_user_prompt(requirement: str, code: str, context: str = "") -> str:
    return f"""REQUIREMENT:
{requirement}

CODE UNDER REVIEW:
```python
{code}
```

ADDITIONAL CONTEXT:
{context or '(none)'}

Judge requirement conformance, not style. Return the requested JSON only."""


def review_with_one(config: ProviderConfig, requirement: str, code: str, context: str = "") -> dict[str, Any]:
    response = call_provider(config, SYSTEM_PROMPT, make_user_prompt(requirement, code, context))
    parsed = parse_json_response(response.text)
    return {
        "provider": response.provider,
        "model": response.model,
        "verdict": parsed["verdict"],
        "reason": str(parsed.get("reason", "")),
        "bug_location": str(parsed.get("bug_location", "")),
        "suggested_fix": str(parsed.get("suggested_fix", "")),
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
        "latency_seconds": response.latency_seconds,
        "raw_text": response.text,
    }


def review_multi_agent(
    providers: list[ProviderConfig], requirement: str, code: str, context: str = ""
) -> dict[str, Any]:
    """Run configured agents concurrently; use a transparent majority vote."""
    results: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=len(providers)) as executor:
        futures = {
            executor.submit(review_with_one, provider, requirement, code, context): provider
            for provider in providers
        }
        for future in as_completed(futures):
            provider = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:  # keep other agent results if one provider fails
                errors.append({"provider": provider.name, "error": f"{type(exc).__name__}: {exc}"})

    counts = {label: sum(1 for item in results if item["verdict"] == label)
              for label in ("CORRECT", "BUGGY", "UNCERTAIN")}
    ranked = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)
    if not results or ranked[0][1] == 0:
        final = "UNCERTAIN"
    elif len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        final = "UNCERTAIN"
    else:
        final = ranked[0][0]

    return {
        "final_verdict": final,
        "vote_counts": counts,
        "agents": sorted(results, key=lambda item: item["provider"]),
        "errors": errors,
        "total_input_tokens": sum(x["input_tokens"] for x in results),
        "total_output_tokens": sum(x["output_tokens"] for x in results),
        "wall_time_seconds": round(max((x["latency_seconds"] for x in results), default=0.0), 4),
    }
