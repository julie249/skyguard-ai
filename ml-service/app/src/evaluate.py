"""
Evaluation harness for AWS anomaly detection.
Computes point-level and event-level Precision, Recall, and F1 scores.
Includes report generator writing to docs/model_report.md and CLI entrypoint.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score

logger = logging.getLogger(__name__)


def extract_events(binary_series: np.ndarray) -> List[Tuple[int, int]]:
    """Extract contiguous spans (start_idx, end_idx) where binary_series is True/1."""
    events: List[Tuple[int, int]] = []
    in_event = False
    start = 0

    for idx, val in enumerate(binary_series):
        if val and not in_event:
            in_event = True
            start = idx
        elif not val and in_event:
            in_event = False
            events.append((start, idx - 1))

    if in_event:
        events.append((start, len(binary_series) - 1))
    return events


def evaluate_metrics(
    y_true: np.ndarray, y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Computes Point-Level and Event-Level Precision, Recall, and F1.
    For event-level:
      An anomaly event is recalled if at least one timestamp within the event span is detected.
      A predicted alarm is precise if it intersects a ground truth anomaly event.
    """
    y_true = np.asarray(y_true, dtype=bool)
    y_pred = np.asarray(y_pred, dtype=bool)

    # Point-level
    p_prec = float(precision_score(y_true, y_pred, zero_division=0))
    p_rec = float(recall_score(y_true, y_pred, zero_division=0))
    p_f1 = float(f1_score(y_true, y_pred, zero_division=0))

    # Event-level
    gt_events = extract_events(y_true)
    pred_events = extract_events(y_pred)

    if not gt_events:
        e_rec = 1.0 if not pred_events else 0.0
    else:
        detected_gt = 0
        for start, end in gt_events:
            if np.any(y_pred[start : end + 1]):
                detected_gt += 1
        e_rec = float(detected_gt / len(gt_events))

    if not pred_events:
        e_prec = 1.0 if not gt_events else 0.0
    else:
        valid_pred = 0
        for start, end in pred_events:
            if np.any(y_true[start : end + 1]):
                valid_pred += 1
        e_prec = float(valid_pred / len(pred_events))

    e_f1 = float((2 * e_prec * e_rec / (e_prec + e_rec)) if (e_prec + e_rec) > 0 else 0.0)

    return {
        "point_precision": round(p_prec, 4),
        "point_recall": round(p_rec, 4),
        "point_f1": round(p_f1, 4),
        "event_precision": round(e_prec, 4),
        "event_recall": round(e_rec, 4),
        "event_f1": round(e_f1, 4),
    }


def generate_report(
    results: Dict[str, Dict[str, Dict[str, float]]],
    output_path: str | Path = "docs/model_report.md",
) -> str:
    """
    Generate markdown report table from results dict:
    results[dataset_label][model_name] = {point_precision, point_recall, ...}
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# SkyGuard AI — Model Evaluation & Benchmark Report",
        "",
        "## Overview",
        "Automated evaluation across multi-station Automatic Weather Station (AWS) datasets.",
        "Both Point-Level and Event-Level Precision, Recall, and F1 metrics are evaluated.",
        "",
        "| Dataset / Rate | Model | Point Prec | Point Rec | Point F1 | Event Prec | Event Rec | Event F1 |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for ds_name, model_dict in results.items():
        for model_name, m in model_dict.items():
            lines.append(
                f"| {ds_name} | {model_name} | {m.get('point_precision', 0):.4f} | "
                f"{m.get('point_recall', 0):.4f} | {m.get('point_f1', 0):.4f} | "
                f"{m.get('event_precision', 0):.4f} | {m.get('event_recall', 0):.4f} | "
                f"{m.get('event_f1', 0):.4f} |"
            )

    lines.extend([
        "",
        "## Methodology",
        "- **Point-Level Evaluation**: Strict timestamp-by-timestamp classification accuracy.",
        "- **Event-Level Evaluation**: Segment-based detection. A sensor fault or weather event spanning several 10-minute intervals is considered successfully caught if alerted during its duration.",
        "- **Sanity Check**: Always-normal baseline scores 0.0 recall, validating the evaluation harness.",
    ])

    report_content = "\n".join(lines)
    out.write_text(report_content, encoding="utf-8")
    return report_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate anomaly detection predictions.")
    parser.add_argument("--data", type=str, required=True, help="Path to labeled CSV data")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    y_true = df["is_anomaly"].fillna(False).values
    # Dummy baseline
    y_pred = np.zeros_like(y_true, dtype=bool)

    metrics = evaluate_metrics(y_true, y_pred)
    print("Baseline Always-Normal Evaluation Metrics:")
    print(json.dumps(metrics, indent=2))
