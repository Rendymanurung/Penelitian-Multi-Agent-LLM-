from __future__ import annotations

from typing import Iterable


def classification_metrics(rows: Iterable[dict]) -> dict:
    """Positive class is CORRECT/conforming, matching the Jin & Chen paper."""
    rows = list(rows)
    tp = fp = tn = fn = 0
    for row in rows:
        truth = row["ground_truth"]  # CORRECT or BUGGY
        predicted = row["predicted"]  # CORRECT, BUGGY, or UNCERTAIN
        if predicted == "UNCERTAIN":
            continue
        actual_positive = truth == "CORRECT"
        predicted_positive = predicted == "CORRECT"
        if actual_positive and predicted_positive:
            tp += 1
        elif not actual_positive and predicted_positive:
            fp += 1  # a buggy implementation was incorrectly accepted
        elif not actual_positive and not predicted_positive:
            tn += 1
        else:
            fn += 1  # a correct implementation was incorrectly rejected

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    fnr = fn / (fn + tp) if fn + tp else 0.0
    return {
        "positive_class": "CORRECT",
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "fpr": round(fpr, 6),
        "fnr": round(fnr, 6),
        "abstentions": sum(1 for row in rows if row["predicted"] == "UNCERTAIN"),
    }
