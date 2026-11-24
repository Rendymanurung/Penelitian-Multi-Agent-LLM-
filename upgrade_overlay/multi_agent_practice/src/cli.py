from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import run_benchmark
from .config import require_providers
from .pr_review import review_diff


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Agent LLM code review research runner")
    sub = parser.add_subparsers(dest="command", required=True)

    bench = sub.add_parser("benchmark", help="Run model judgments on a paired JSON/JSONL dataset")
    bench.add_argument("--dataset", required=True)
    bench.add_argument("--mode", choices=["single", "multi"], default="multi")
    bench.add_argument("--output-dir", default="results")
    bench.add_argument("--limit", type=int, default=0, help="0 = all paired tasks")
    bench.add_argument("--minimum-providers", type=int, default=1)

    review = sub.add_parser("review-diff", help="Review a GitHub Pull Request diff")
    review.add_argument("--diff-file", required=True)
    review.add_argument("--requirement", default="")
    review.add_argument("--minimum-providers", type=int, default=2)

    args = parser.parse_args()
    minimum = args.minimum_providers
    if args.command == "benchmark" and args.mode == "multi":
        minimum = max(minimum, 2)
    providers = require_providers(minimum)

    if args.command == "benchmark":
        if args.mode == "single":
            providers = providers[:1]
        run_benchmark(args.dataset, providers, args.output_dir, args.mode, args.limit)
    elif args.command == "review-diff":
        result = review_diff(args.diff_file, args.requirement, providers)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        # Uncertain is deliberately non-blocking; a definitive BUGGY result fails the job.
        if result["final_verdict"] == "BUGGY":
            raise SystemExit(1)


if __name__ == "__main__":
    main()
