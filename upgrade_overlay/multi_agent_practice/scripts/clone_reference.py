from __future__ import annotations

import subprocess
from pathlib import Path

REPO = "https://github.com/HollinJ3177/Are-LLMs-Reliable-Code-Reviewers-Systematic-Overcorrection-in-Requirement-Conformance-Judgement.git"
DEST = Path("references/jin_chen_2026")


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        print(f"Reference repository already exists at {DEST}")
    else:
        subprocess.run(["git", "clone", "--depth", "1", REPO, str(DEST)], check=True)
    dataset_dir = DEST / "dataset"
    print("\nCandidate dataset files:")
    found = False
    for path in sorted(dataset_dir.rglob("*")) if dataset_dir.exists() else []:
        if path.is_file() and path.suffix.lower() in {".json", ".jsonl"}:
            print(path)
            found = True
    if not found:
        print("No .json/.jsonl files found under the reference dataset directory.")
        print("Inspect the dataset preparation scripts and README in", DEST)


if __name__ == "__main__":
    main()
