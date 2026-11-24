# Multi-Agent LLM Code Review Research — implementation starter

This package upgrades the original `multi_agent_practice` simulation into an API-backed research starter. It is **not yet a completed reproduction of the complete Fix-Guided Verification Filter paper**: the first implementation stage provides real provider calls, a transparent multi-agent majority vote, paired-dataset loading, baseline metrics, and GitHub Actions entry points. The execution-based FGV stage (including spec-constrained augmented tests and safe sandboxing) must be implemented and validated next before claiming the full method is reproduced.

## Architecture in this starter

- OpenAI API: default `gpt-6.2-sol`
- Gemini API: default `gemini-3.8-flash`
- Groq API: default `qwen/qwen3.8-27b`
- Multi-agent: independent parallel reviews; final verdict is the majority vote; ties / no results become `UNCERTAIN`.
- Single-agent baseline: uses the first configured provider.
- Dataset: paired canonical and buggy implementations in JSON/JSONL.
- GitHub Actions: PR diff review and manually triggered benchmark workflow.

Provider and model IDs are configurable in `.env` or GitHub repository variables. Verify access to each model in your own API account before formal data collection. A provider account may have model-specific quotas or billing requirements.

## 1. Local setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and fill the API keys you have. Do not paste keys into source files, chat, screenshots, or Git commits. For a 3-agent run, provide all three keys. For a first smoke test, one configured provider is enough.

## 2. Verify provider connectivity

Run a tiny benchmark after placing a valid dataset file. The configured model IDs are defaults, not guarantees of account entitlement. If a model is unavailable, change its ID in `.env` after checking the provider's current model catalogue.

Official catalogues:

- OpenAI: https://developers.openai.com/api/docs/models
- Gemini: https://ai.google.dev/gemini-api/docs/models
- Groq: https://console.groq.com/docs/models

## 3. Fetch the paper's reference dataset/code package

```powershell
python scripts/clone_reference.py
```

The script clones the authors' reproduction repository into `references/jin_chen_2026/` and lists `.json` / `.jsonl` dataset candidates. Inspect these files and copy the proposal-approved HumanEval-X-Bugs and Buggy-MBPP files into `data/raw/`.

Reference paper and reproduction package:
https://link.springer.com/article/10.1007/s10515-026-00638-5
https://github.com/HollinJ3177/Are-LLMs-Reliable-Code-Reviewers-Systematic-Overcorrection-in-Requirement-Conformance-Judgement

## 4. Run a baseline smoke test

```powershell
python -m src.cli benchmark --dataset data/raw/humaneval_x_bugs.jsonl --mode single --limit 2
```

Run the 3-agent version after configuring all providers:

```powershell
python -m src.cli benchmark --dataset data/raw/humaneval_x_bugs.jsonl --mode multi --limit 2
```

Repeat for Buggy-MBPP. Start with `--limit 2` or `--limit 5` to check data shape, API permissions, model output parsing, and costs. Only then run the complete benchmark.

Each paired task is evaluated twice: once with its canonical solution (ground truth `CORRECT`) and once with its buggy solution (ground truth `BUGGY`). Results are saved as JSONL and a summary JSON in `results/`.

### Metric convention

This project follows the positive-class convention used in the Jin & Chen study: **positive = canonical/correct implementation**. Therefore, rejecting correct code is FN / contributes to FNR (the over-correction measure); accepting buggy code is FP / contributes to FPR (false acceptance). This convention must be stated clearly in the thesis because some code-defect studies instead define `BUGGY` as the positive class.

## 5. GitHub repository secrets and variables

In GitHub, open Settings → Secrets and variables → Actions.

Add repository secrets:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `GROQ_API_KEY`

Optional repository variables:

- `OPENAI_MODEL`
- `GEMINI_MODEL`
- `GROQ_MODEL`

Never commit `.env`. Never print environment variables in Actions logs.

## 6. GitHub Actions

Two workflows are included:

- `.github/workflows/pr-review.yml`: runs a multi-agent review over changed Python files on PR open/update. It reads the diff and PR text only; it does not execute PR code.
- `.github/workflows/benchmark.yml`: manually runs the selected paired dataset and uploads JSONL/summary artifacts.

The initial PR workflow is a review proof-of-concept, not yet the proposal's final full workflow. It does not post comments and it does not run FGV on arbitrary PR code. This avoids executing untrusted code in a runner that has API secrets.

## 7. Important research limitations / next implementation stage

1. The current benchmark runner records model verdicts, raw responses, latency, token use, and classification metrics. It does **not** yet run model-generated repair code.
2. The complete Fix-Guided Verification Filter requires original-vs-fix execution using benchmark tests plus spec-constrained augmented tests and up to K=2 re-evaluation rounds. Implement this in an isolated sandbox (container, no network, low privileges, resource and timeout limits) before claiming the filter is fully integrated.
3. The current `UNCERTAIN` outputs are excluded from confusion-matrix denominators and reported as abstentions; document this decision or change it before the formal run.
4. Public real-world Pull Requests need a trustworthy ground-truth labeling protocol. `merged` status alone is not proof that a change is correct or buggy.
5. For fair comparison, keep datasets, prompts, run limits, sampling parameters, model versions, and repeated-run policy fixed and logged across configurations.
6. The two-model / three-model comparison and any change from the models specified in the proposal should be approved by the supervisor and reflected in the methodology chapter.

## 8. Run basic tests

```powershell
python -m unittest discover -s tests -v
```
