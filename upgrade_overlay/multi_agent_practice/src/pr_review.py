from __future__ import annotations

from pathlib import Path
from typing import Any

from .agents import review_multi_agent
from .config import ProviderConfig


def review_diff(diff_path: str, requirement: str, providers: list[ProviderConfig]) -> dict[str, Any]:
    diff = Path(diff_path).read_text(encoding="utf-8", errors="replace")
    if not diff.strip():
        raise ValueError("The PR diff is empty. Check the base/head commit range and Python file filters.")
    if len(diff) > 100_000:
        diff = diff[:100_000] + "\n\n[DIFF TRUNCATED at 100,000 characters]"
    return review_multi_agent(
        providers,
        requirement=requirement or "Review this pull request for functional defects and requirement mismatches.",
        code=diff,
        context="The input is a unified Git diff, not a complete standalone Python file. Only report issues supported by the changed lines and available context.",
    )
