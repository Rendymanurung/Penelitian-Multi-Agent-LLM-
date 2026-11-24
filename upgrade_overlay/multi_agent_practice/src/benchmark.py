from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .agents import review_multi_agent, review_with_one
from .config import ProviderConfig
from .dataset import join_declaration, load_paired_dataset
from .metrics import classification_metrics


def run_benchmark(
    dataset_path: str,
    providers: list[ProviderConfig],
    output_dir: str = "results",
    mode: str = "multi",
    limit: int = 0,
) -> dict[str, Any]:
    tasks = load_paired_dataset(dataset_path)
    if limit > 0:
        tasks = tasks[:limit]
    if mode == "single" and not providers:
        raise ValueError("Single-agent mode requires one configured provider")
    if mode not in {"single", "multi"}:
        raise ValueError("mode must be 'single' or 'multi'")

    # In single mode, use the first configured provider. In multi mode, use all.
    selected = providers[:1] if mode == "single" else providers
    rows: list[dict[str, Any]] = []
    started_all = time.perf_counter()
    for task in tasks:
        variants = [
            ("canonical", "CORRECT", join_declaration(task.declaration, task.canonical_solution)),
            ("buggy", "BUGGY", join_declaration(task.declaration, task.buggy_solution)),
        ]
        for variant, ground_truth, code in variants:
            context = "\n".join(x for x in [task.test, task.example_test] if x)
            if mode == "single":
                result = review_with_one(selected[0], task.requirement, code, context)
                result = {
                    "final_verdict": result["verdict"],
                    "agents": [result],
                    "total_input_tokens": result["input_tokens"],
                    "total_output_tokens": result["output_tokens"],
                    "wall_time_seconds": result["latency_seconds"],
                }
            else:
                result = review_multi_agent(selected, task.requirement, code, context)
            rows.append({
                "task_id": task.task_id,
                "variant": variant,
                "ground_truth": ground_truth,
                "predicted": result["final_verdict"],
                "agent_results": result["agents"],
                "errors": result.get("errors", []),
                "input_tokens": result["total_input_tokens"],
                "output_tokens": result["total_output_tokens"],
                "wall_time_seconds": result["wall_time_seconds"],
                "test_available": bool(task.test or task.example_test),
                "filter_status": "NOT_RUN_IN_INITIAL_API_BENCHMARK",
            })
            print(f"[{task.task_id} / {variant}] truth={ground_truth} prediction={result['final_verdict']}")

    total_wall = round(time.perf_counter() - started_all, 4)
    for row in rows:
        row["experiment_mode"] = mode

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    stem = f"{Path(dataset_path).stem}_{mode}_{stamp}"
    jsonl_path = out / f"{stem}.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    metrics = classification_metrics(rows)
    summary = {
        "dataset": str(dataset_path),
        "mode": mode,
        "models": [{"provider": p.name, "model": p.model} for p in selected],
        "task_count": len(tasks),
        "sample_count": len(rows),
        "total_wall_time_seconds": total_wall,
        "total_input_tokens": sum(row["input_tokens"] for row in rows),
        "total_output_tokens": sum(row["output_tokens"] for row in rows),
        "metrics": metrics,
        "raw_results": jsonl_path.name,
    }
    summary_path = out / f"{stem}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nSUMMARY")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary
