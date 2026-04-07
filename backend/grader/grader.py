"""
TruthGuardEnv Grader — deterministic, reproducible scoring.
"""
from typing import Dict, List


def compute_score(
    predicted_harmful: List[str],
    true_harmful: List[str],
    risk_estimate: float,
    true_risk: float,
    verdict: str,
    true_verdict: str,
) -> Dict[str, float]:
    """
    Compute the final grader score.

    Final = 0.5 * F1 + 0.3 * Calibration + 0.2 * Accuracy
    """
    # ── Issue F1 ──
    pred_set = set(predicted_harmful)
    true_set = set(true_harmful)
    tp = len(pred_set & true_set)
    fp = len(pred_set - true_set)
    fn = len(true_set - pred_set)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    # ── Risk Calibration (1 - |estimate - truth|) ──
    calibration = max(0.0, 1.0 - abs(risk_estimate - true_risk))

    # ── Verdict Accuracy ──
    accuracy = 1.0 if verdict.upper() == true_verdict.upper() else 0.0

    # ── Final weighted score ──
    final = 0.5 * f1 + 0.3 * calibration + 0.2 * accuracy
    final = round(max(0.0, min(1.0, final)), 4)

    return {
        "issue_f1": round(f1, 4),
        "risk_calibration": round(calibration, 4),
        "verdict_accuracy": round(accuracy, 4),
        "final_score": final,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
    }
