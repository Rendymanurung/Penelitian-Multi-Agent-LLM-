import json
import tempfile
import unittest
from pathlib import Path

from src.dataset import load_paired_dataset, join_declaration
from src.metrics import classification_metrics


class DatasetTests(unittest.TestCase):
    def test_load_jsonl_paired_record(self):
        record = {
            "task_id": "t1",
            "text": "Return an even-number list.",
            "declaration": "def f(xs):",
            "canonical_solution": "    return [x for x in xs if x % 2 == 0]",
            "buggy_solution": "    return [x for x in xs if x % 2 == 1]",
            "test": "assert f([1, 2]) == [2]",
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "data.jsonl"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            tasks = load_paired_dataset(path)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_id, "t1")
        self.assertIn("def f", join_declaration(tasks[0].declaration, tasks[0].canonical_solution))

    def test_metrics_positive_class_correct(self):
        rows = [
            {"ground_truth": "CORRECT", "predicted": "CORRECT"},
            {"ground_truth": "CORRECT", "predicted": "BUGGY"},
            {"ground_truth": "BUGGY", "predicted": "CORRECT"},
            {"ground_truth": "BUGGY", "predicted": "BUGGY"},
        ]
        result = classification_metrics(rows)
        self.assertEqual((result["tp"], result["fp"], result["tn"], result["fn"]), (1, 1, 1, 1))
        self.assertEqual(result["fnr"], 0.5)
        self.assertEqual(result["fpr"], 0.5)


if __name__ == "__main__":
    unittest.main()
