from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RiskAdjustmentResult:
    adjustment: float
    reasons: List[str]


class RiskRules:
    """
    Additive Hybrid Risk Rules

    Purpose:
    - Apply small rule-based nudges on top of model probability
    - Keep model as the primary signal
    - Return adjustment value and human-readable reasons
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    # =========================
    # Logging
    # =========================
    def _log(self, message: str):
        if self.verbose:
            print(f"[RiskRules] {datetime.now().strftime('%H:%M:%S')} | {message}")

    # =========================
    # Public API
    # =========================
    def compute_additive_adjustment(
        self,
        payload: Dict[str, Any],
        base_probability: Optional[float] = None,
    ) -> RiskAdjustmentResult:
        self._log("Starting additive risk adjustment...")

        if not isinstance(payload, dict):
            raise TypeError("payload must be a dictionary.")

        adjustment = 0.0
        reasons: List[str] = []

        age = self._safe_float(payload.get("age"))
        bmi = self._safe_float(payload.get("bmi"))
        waist = self._safe_float(payload.get("waist_circumference"))
        systolic = self._safe_float(payload.get("systolic_bp"))
        diastolic = self._safe_float(payload.get("diastolic_bp"))
        glucose = self._safe_float(payload.get("blood_glucose_level"))

        hypertension = self._safe_int(payload.get("hypertension"), default=0)
        heart_disease = self._safe_int(payload.get("heart_disease"), default=0)
        family_history = self._safe_int(payload.get("family_history_diabetes"), default=0)

        smoking = str(payload.get("smoking_history", "")).strip().lower()
        activity = str(payload.get("physical_activity_level", "")).strip().lower()

        # =========================
        # Family history
        # =========================
        if family_history == 1:
            adjustment += 0.02
            reasons.append("Family history of diabetes increases baseline risk.")

        # =========================
        # Hypertension / cardiovascular
        # =========================
        if hypertension == 1:
            adjustment += 0.015
            reasons.append("Hypertension is associated with elevated diabetes risk.")

        if heart_disease == 1:
            adjustment += 0.01
            reasons.append("History of heart disease adds cardiometabolic risk.")

        if systolic is not None and systolic >= 140:
            adjustment += 0.01
            reasons.append("High systolic blood pressure adds cardiometabolic risk.")
        elif systolic is not None and systolic < 110:
            adjustment -= 0.003

        if diastolic is not None and diastolic >= 90:
            adjustment += 0.008
            reasons.append("High diastolic blood pressure slightly increases risk.")

        # =========================
        # Age
        # =========================
        if age is not None:
            if age >= 60:
                adjustment += 0.015
                reasons.append("Older age group raises underlying risk.")
            elif age >= 45:
                adjustment += 0.01
                reasons.append("Age above 45 contributes additional risk.")
            elif age < 25:
                adjustment -= 0.005

        # =========================
        # BMI
        # =========================
        if bmi is not None:
            if bmi >= 35:
                adjustment += 0.025
                reasons.append("Severe obesity strongly increases metabolic risk.")
            elif bmi >= 30:
                adjustment += 0.018
                reasons.append("Obesity increases metabolic risk.")
            elif bmi >= 25:
                adjustment += 0.01
                reasons.append("Overweight status slightly increases risk.")
            elif bmi < 18.5:
                adjustment -= 0.005

        # =========================
        # Waist circumference
        # =========================
        if waist is not None:
            if waist >= 100:
                adjustment += 0.015
                reasons.append("High waist circumference suggests central obesity.")
            elif waist >= 90:
                adjustment += 0.008
                reasons.append("Moderately elevated waist circumference adds risk.")

        # =========================
        # Blood glucose
        # =========================
        if glucose is not None:
            if glucose >= 200:
                adjustment += 0.05
                reasons.append("Very high blood glucose strongly elevates risk.")
            elif glucose >= 140:
                adjustment += 0.035
                reasons.append("Elevated blood glucose substantially increases risk.")
            elif glucose >= 100:
                adjustment += 0.015
                reasons.append("Borderline high blood glucose adds some risk.")
            elif glucose < 85:
                adjustment -= 0.005

        # =========================
        # Smoking
        # =========================
        if smoking in {"current", "ever", "former"}:
            adjustment += 0.008
            reasons.append("Smoking history slightly increases metabolic risk.")

        # =========================
        # Physical activity
        # =========================
        if activity == "low":
            adjustment += 0.01
            reasons.append("Low physical activity reduces metabolic protection.")
        elif activity == "high":
            adjustment -= 0.008
            reasons.append("High physical activity slightly reduces overall risk.")

        # =========================
        # Probability-aware moderation
        # =========================
        if base_probability is not None:
            base_probability = float(base_probability)

            if base_probability >= 0.80:
                adjustment *= 0.35
            elif base_probability >= 0.65:
                adjustment *= 0.50
            elif base_probability >= 0.50:
                adjustment *= 0.70
            elif base_probability <= 0.20:
                adjustment *= 0.60

        # keep additive effect bounded
        adjustment = max(-0.05, min(0.08, adjustment))

        self._log(f"Computed adjustment: {adjustment:+.4f}")
        self._log(f"Reasons count: {len(reasons)}")

        return RiskAdjustmentResult(
            adjustment=round(adjustment, 4),
            reasons=reasons,
        )

    # =========================
    # Business mapping helpers
    # =========================
    def map_risk_level(self, probability: float) -> str:
        if probability < 0.20:
            return "Low"
        if probability < 0.40:
            return "Mild"
        if probability < 0.60:
            return "Moderate"
        if probability < 0.80:
            return "High"
        return "Very High"

    def map_label(self, adjusted_predicted_class: int) -> str:
        return "At Risk" if adjusted_predicted_class == 1 else "Lower Risk"

    def build_message(
        self,
        adjusted_probability: float,
        threshold: float,
        risk_level: str,
        label: str,
    ) -> str:
        percent = adjusted_probability * 100

        if adjusted_probability >= threshold:
            return (
                f"The model estimates a {percent:.1f}% diabetes risk, "
                f"which is above the decision threshold ({threshold:.2f}). "
                f"Overall assessment: {label} ({risk_level})."
            )

        return (
            f"The model estimates a {percent:.1f}% diabetes risk, "
            f"which is below the decision threshold ({threshold:.2f}). "
            f"Overall assessment: {label} ({risk_level})."
        )

    # =========================
    # Safe converters
    # =========================
    def _safe_float(self, value: Any, default=None):
        try:
            if value is None or value == "":
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _safe_int(self, value: Any, default=0):
        try:
            if value is None or value == "":
                return default
            return int(value)
        except (TypeError, ValueError):
            return default


# =========================
# Convenience functions
# =========================
def compute_additive_adjustment(
    payload: Dict[str, Any],
    verbose: bool = True,
    base_probability: Optional[float] = None,
) -> RiskAdjustmentResult:
    rules = RiskRules(verbose=verbose)
    return rules.compute_additive_adjustment(
        payload=payload,
        base_probability=base_probability,
    )


def map_risk_level(probability: float, verbose: bool = False) -> str:
    rules = RiskRules(verbose=verbose)
    return rules.map_risk_level(probability)


def map_label(adjusted_predicted_class: int, verbose: bool = False) -> str:
    rules = RiskRules(verbose=verbose)
    return rules.map_label(adjusted_predicted_class)


def build_risk_message(
    adjusted_probability: float,
    threshold: float,
    risk_level: str,
    label: str,
    verbose: bool = False,
) -> str:
    rules = RiskRules(verbose=verbose)
    return rules.build_message(
        adjusted_probability=adjusted_probability,
        threshold=threshold,
        risk_level=risk_level,
        label=label,
    )


# =========================
# Quick test
# =========================
if __name__ == "__main__":
    sample_payload = {
        "gender": "male",
        "age": 52,
        "hypertension": 1,
        "heart_disease": 0,
        "family_history_diabetes": 1,
        "smoking_history": "former",
        "height": 170,
        "weight": 85,
        "bmi": 29.41,
        "systolic_bp": 145,
        "diastolic_bp": 92,
        "waist_circumference": 101,
        "blood_glucose_level": 152,
        "physical_activity_level": "low",
    }

    result = compute_additive_adjustment(
        sample_payload,
        verbose=True,
        base_probability=0.72,
    )

    print("\n=== FINAL ADJUSTMENT RESULT ===")
    print("adjustment:", result.adjustment)
    print("reasons:")
    for reason in result.reasons:
        print("-", reason)