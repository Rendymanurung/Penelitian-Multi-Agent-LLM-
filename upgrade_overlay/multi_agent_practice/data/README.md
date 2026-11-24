# Dataset placement

Do not invent or manually relabel benchmark records. Use the paired benchmark data and preprocessing code published by Jin & Chen (2026):

https://github.com/HollinJ3177/Are-LLMs-Reliable-Code-Reviewers-Systematic-Overcorrection-in-Requirement-Conformance-Judgement

The paper/reproduction package describes records with fields such as `task_id`, requirement text (`text`/`prompt`/`requirement`), optional `declaration`, `canonical_solution`, `buggy_solution`, and optional `test` / `example_test`.

## Fetch the reference package

From the repository root:

```bash
python scripts/clone_reference.py
```

Then inspect the printed `.json`/`.jsonl` paths under `references/jin_chen_2026/dataset/`.

Copy only the datasets allowed by the approved proposal into `data/raw/` (HumanEval-X-Bugs and Buggy-MBPP). The article also discusses QuixBugs, but it is outside the current proposal's stated scope; do not include it unless the proposal is amended and approved.

Expected normalized paired record fields:

```json
{
  "task_id": "example-id",
  "text": "Natural language requirement...",
  "declaration": "def function_name(...):",
  "canonical_solution": "...",
  "buggy_solution": "...",
  "test": "assert ..."
}
```

The loader accepts `.json` and `.jsonl`. Run a small smoke test before a full benchmark.

Dataset files are excluded from Git by default to avoid accidentally committing large or licensed data. Keep a local copy or use a documented dataset download step in CI.
