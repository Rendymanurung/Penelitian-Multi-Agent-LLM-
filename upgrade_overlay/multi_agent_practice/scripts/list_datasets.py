from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="List JSON/JSONL dataset files in a directory")
    parser.add_argument("--root", default="references/jin_chen_2026/dataset")
    args = parser.parse_args()
    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Dataset directory not found: {root}")
    files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".json", ".jsonl"})
    if not files:
        print(f"No JSON/JSONL files found under {root}")
        return
    print("Dataset files (copy one exact path to the workflow_dispatch dataset_path input):")
    for item in files:
        print(item.as_posix())


if __name__ == "__main__":
    main()
