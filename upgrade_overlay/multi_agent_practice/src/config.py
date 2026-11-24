from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    api_key: str
    model: str


def configured_providers() -> list[ProviderConfig]:
    """Return only providers whose API keys are present."""
    candidates = [
        ProviderConfig("openai", os.getenv("OPENAI_API_KEY", "").strip(), os.getenv("OPENAI_MODEL", "gpt-6.2-sol").strip()),
        ProviderConfig("gemini", os.getenv("GEMINI_API_KEY", "").strip(), os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()),
        ProviderConfig("groq", os.getenv("GROQ_API_KEY", "").strip(), os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()),
    ]
    return [p for p in candidates if p.api_key and p.model]


def require_providers(minimum: int = 1) -> list[ProviderConfig]:
    providers = configured_providers()
    if len(providers) < minimum:
        names = ", ".join(p.name.upper() for p in providers) or "none"
        raise RuntimeError(
            f"Need at least {minimum} configured API provider(s); found {len(providers)} ({names}). "
            "Set API keys in .env locally or GitHub Actions Secrets."
        )
    return providers
