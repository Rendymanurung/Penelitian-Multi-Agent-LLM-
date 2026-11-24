from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


@dataclass
class PairedTask:
    task_id: str
    requirement: str
    canonical_solution: str
    buggy_solution: str
    declaration: str = ""
    test: str = ""
    example_test: str = ""
    source_fields: dict[str, Any] | None = None


def _first(record: dict[str, Any], names: tuple[str, ...], default: Any = "") -> Any:
    for name in names:
        value = record.get(name)
        if value is not None and value != "":
            return value
    return default


def _records(path: Path) -> Iterator[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if line.strip():
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc
                    if isinstance(item, dict):
                        yield item
    elif path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            yield from (x for x in data if isinstance(x, dict))
        elif isinstance(data, dict):
            # Accept common wrappers used for benchmark exports.
            for key in ("data", "records", "examples", "tasks"):
                if isinstance(data.get(key), list):
                    yield from (x for x in data[key] if isinstance(x, dict))
                    return
            yield data
    else:
        raise ValueError("Dataset must be a .json or .jsonl file")


def load_paired_dataset(path: str | Path) -> list[PairedTask]:
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    tasks: list[PairedTask] = []
    for index, record in enumerate(_records(dataset_path), start=1):
        requirement = _first(record, ("text", "prompt", "requirement", "description"))
        canonical = _first(record, ("canonical_solution", "correct_solution", "solution"))
        buggy = _first(record, ("buggy_solution", "incorrect_solution"))
        if not requirement or not canonical or not buggy:
            continue
        tasks.append(PairedTask(
            task_id=str(_first(record, ("task_id", "id", "problem_id"), f"row-{index}")),
            requirement=str(requirement),
            canonical_solution=str(canonical),
            buggy_solution=str(buggy),
            declaration=str(_first(record, ("declaration", "signature"))),
            test=str(_first(record, ("test", "tests"))),
            example_test=str(_first(record, ("example_test", "example_tests"))),
            source_fields=record,
        ))
    if not tasks:
        raise ValueError(
            "No paired records found. Expected task_id, requirement/text, canonical_solution, "
            "and buggy_solution. Check the selected source dataset file."
        )
    return tasks


def join_declaration(declaration: str, solution: str) -> str:
    if not declaration.strip() or solution.lstrip().startswith(("def ", "async def ", "class ", "import ", "from ")):
        return solution
    return declaration.rstrip() + "\n" + solution.lstrip()
