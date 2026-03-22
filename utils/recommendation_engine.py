from datetime import datetime
from typing import Any, Dict, List


class RecommendationEngine:
    """
    Rule-based explanation engine for AI Diabetes Screening System.

    Inputs:
        - normalized_input: dict
        - prediction_result: dict from predictor.py

    Outputs:
        {
            "clinical_flags": [...],
            "key_risk_factors": [...],
            "recommendations": [...],
            "short_interpretation": "..."
        }
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    # =========================
    # Logging
    # =========================
    def _log(self, message: str):
        if self.verbose:
            print(f"[RecommendationEngine] {datetime.now().strftime('%H:%M:%S')} | {message}")

    # =========================
    # Public API
    # =========================
    def generate(
        self,
        normalized_input: Dict[str, Any],
        prediction_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        self._log("Starting recommendation engine...")

        self._validate_inputs(normalized_input, prediction_result)

        key_risk_factors = self._extract_key_risk_factors(normalized_input)
        clinical_flags = self._extract_clinical_flags(normalized_input)

        recommendations = self._generate_recommendations(
            normalized_input=normalized_input,
            prediction_result=prediction_result,
            key_risk_factors=key_risk_factors,
            clinical_flags=clinical_flags,
        )

        short_interpretation = self._generate_short_interpretation(
            normalized_input=normalized_input,
            prediction_result=prediction_result,
            key_risk_factors=key_risk_factors,
            clinical_flags=clinical_flags,
        )

        result = {
            "clinical_flags": clinical_flags,
            "key_risk_factors": key_risk_factors,
            "recommendations": recommendations,
            "short_interpretation": short_interpretation,
        }

        self._log("Recommendation engine completed successfully.")
        self._print_summary(result)
        return result

    # =========================
    # Validation
    # =========================
    def _validate_inputs(
        self,
        normalized_input: Dict[str, Any],
        prediction_result: Dict[str, Any],
    ):
        required_input_keys = {
            "age",
            "gender",
            "hypertension",
            "heart_disease",
            "family_history_diabetes",
            "smoking_history",
            "height",
            "weight",
            "systolic_bp",
            "diastolic_bp",
            "waist_circumference",
            "blood_glucose_level",
            "physical_activity_level",
        }

        required_prediction_keys = {
            "predicted_class",
            "prediction_code",
            "prediction_label",
            "screening_result",
            "threshold",
        }

        missing_input = [k for k in required_input_keys if k not in normalized_input]
        missing_prediction = [k for k in required_prediction_keys if k not in prediction_result]

        if missing_input:
            raise ValueError(f"Missing normalized_input keys: {missing_input}")

        if missing_prediction:
            raise ValueError(f"Missing prediction_result keys: {missing_prediction}")

        self._log("Input validation passed.")

    # =========================
    # Factor Extraction
    # =========================
    def _extract_key_risk_factors(self, data: Dict[str, Any]) -> List[str]:
        factors: List[str] = []

        bmi = self._calculate_bmi(data["height"], data["weight"])
        glucose = float(data["blood_glucose_level"])
        age = float(data["age"])
        waist = float(data["waist_circumference"])
        sbp = float(data["systolic_bp"])
        dbp = float(data["diastolic_bp"])

        glucose_test_type = str(data.get("glucose_test_type", "random")).lower()

        # Blood glucose
        if glucose_test_type == "fasting":
            if glucose >= 126:
                factors.append("Fasting glucose in diabetes-range threshold")
            elif glucose >= 100:
                factors.append("Fasting glucose in prediabetes range")
        else:
            if glucose >= 200:
                factors.append("Very high random blood glucose")
            elif glucose >= 140:
                factors.append("Elevated random blood glucose")

        # BMI
        if bmi >= 30:
            factors.append("Obesity-level BMI")
        elif bmi >= 25:
            factors.append("High BMI")

        # Hypertension / BP
        if int(data["hypertension"]) == 1:
            factors.append("Hypertension history")
        elif sbp >= 140 or dbp >= 90:
            factors.append("Elevated blood pressure")

        # Waist circumference
        if self._is_high_waist(data["gender"], waist):
            factors.append("High waist circumference")

        # Age
        if age >= 60:
            factors.append("Older age group")
        elif age >= 45:
            factors.append("Age 45 years or older")

        # Heart disease
        if int(data["heart_disease"]) == 1:
            factors.append("History of heart disease")

        # Family history
        if int(data["family_history_diabetes"]) == 1:
            factors.append("Family history of diabetes")

        # Smoking
        if str(data["smoking_history"]).lower() in {"current", "ever", "former"}:
            factors.append("Smoking-related risk")

        # Physical activity
        if str(data["physical_activity_level"]).lower() == "low":
            factors.append("Low physical activity level")

        return self._deduplicate(factors)

    def _extract_clinical_flags(self, data: Dict[str, Any]) -> List[str]:
        flags: List[str] = []

        bmi = self._calculate_bmi(data["height"], data["weight"])
        glucose = float(data["blood_glucose_level"])
        sbp = float(data["systolic_bp"])
        dbp = float(data["diastolic_bp"])
        waist = float(data["waist_circumference"])
        gender = str(data["gender"]).lower()
        glucose_test_type = str(data.get("glucose_test_type", "random")).lower()

        # Glucose
        if glucose_test_type == "fasting":
            if glucose >= 126:
                flags.append("Fasting blood glucose is in the diabetes-range threshold (>=126 mg/dL).")
            elif glucose >= 100:
                flags.append("Fasting blood glucose is in the prediabetes range (100-125 mg/dL).")
        else:
            if glucose >= 200:
                flags.append("Random blood glucose is in a very high range (>=200 mg/dL).")
            elif glucose >= 140:
                flags.append("Random blood glucose is elevated and should be monitored.")

        # BMI
        if bmi >= 30:
            flags.append("BMI is in the obesity range.")
        elif bmi >= 25:
            flags.append("BMI is above the recommended healthy range.")

        # BP
        if sbp >= 140 or dbp >= 90:
            flags.append("Blood pressure is in the high range.")
        elif sbp >= 130 or dbp >= 80:
            flags.append("Blood pressure is above optimal range.")

        # Waist
        if self._is_high_waist(gender, waist):
            flags.append("Waist circumference suggests increased metabolic risk.")

        # Combined risk clustering
        metabolic_count = 0
        if bmi >= 25:
            metabolic_count += 1
        if self._is_high_waist(gender, waist):
            metabolic_count += 1
        if sbp >= 130 or dbp >= 80 or int(data["hypertension"]) == 1:
            metabolic_count += 1
        if (
            (glucose_test_type == "fasting" and glucose >= 100)
            or (glucose_test_type != "fasting" and glucose >= 140)
        ):
            metabolic_count += 1

        if metabolic_count >= 3:
            flags.append("Multiple metabolic risk indicators are present and warrant closer follow-up.")

        return self._deduplicate(flags)

    # =========================
    # Recommendation Logic
    # =========================
    def _generate_recommendations(
        self,
        normalized_input: Dict[str, Any],
        prediction_result: Dict[str, Any],
        key_risk_factors: List[str],
        clinical_flags: List[str],
    ) -> List[str]:
        recommendations: List[str] = []

        predicted_class = int(prediction_result["predicted_class"])
        prediction_code = str(prediction_result["prediction_code"]).lower()
        factor_set = set(key_risk_factors)

        # Base recommendation from screening result
        if predicted_class == 1 or prediction_code == "positive":
            recommendations.append(
                "Consider confirmatory diabetes screening or follow-up laboratory testing with a healthcare professional."
            )
            recommendations.append(
                "This screening result should be reviewed together with clinical history, symptoms, and laboratory evaluation."
            )
        else:
            recommendations.append(
                "Current screening does not strongly suggest diabetes, but ongoing preventive monitoring is still recommended."
            )

        # Clinical flags
        if clinical_flags:
            recommendations.append(
                "Because clinical warning signs are present, consider closer follow-up even if this is only a screening result."
            )

        # Factor-specific recommendations
        if (
            "Fasting glucose in diabetes-range threshold" in factor_set
            or "Fasting glucose in prediabetes range" in factor_set
            or "Very high random blood glucose" in factor_set
            or "Elevated random blood glucose" in factor_set
        ):
            recommendations.append(
                "Monitor blood glucose trends and review diet, meal timing, and follow-up testing strategy."
            )

        if "High BMI" in factor_set or "Obesity-level BMI" in factor_set:
            recommendations.append(
                "Weight management through balanced nutrition and regular physical activity may help reduce diabetes risk."
            )

        if "Low physical activity level" in factor_set:
            recommendations.append(
                "Increase physical activity gradually toward a consistent weekly routine when appropriate."
            )

        if "Hypertension history" in factor_set or "Elevated blood pressure" in factor_set:
            recommendations.append(
                "Monitor blood pressure and address cardiometabolic risk factors in parallel."
            )

        if "Smoking-related risk" in factor_set:
            recommendations.append(
                "Reducing or stopping smoking may improve long-term cardiometabolic health."
            )

        if "Family history of diabetes" in factor_set:
            recommendations.append(
                "Because of family history, periodic diabetes screening remains important over time."
            )

        if "High waist circumference" in factor_set:
            recommendations.append(
                "Reducing abdominal adiposity may help lower metabolic risk."
            )

        if "History of heart disease" in factor_set:
            recommendations.append(
                "Coordinate diabetes screening with cardiovascular follow-up when relevant."
            )

        # Lower-concern case
        if prediction_code == "negative" and len(clinical_flags) == 0 and len(key_risk_factors) <= 1:
            recommendations.append(
                "Maintain healthy lifestyle habits and continue routine preventive health checks."
            )

        return self._deduplicate(recommendations)

    # =========================
    # Interpretation
    # =========================
    def _generate_short_interpretation(
        self,
        normalized_input: Dict[str, Any],
        prediction_result: Dict[str, Any],
        key_risk_factors: List[str],
        clinical_flags: List[str],
    ) -> str:
        prediction_label = str(prediction_result["prediction_label"])
        screening_result = str(prediction_result["screening_result"])
        prediction_code = str(prediction_result["prediction_code"]).lower()

        factor_phrase = (
            ", ".join(key_risk_factors[:3])
            if key_risk_factors
            else "no major risk factors were highlighted"
        )

        if prediction_code == "positive":
            text = (
                f"The model classified this case as {prediction_label} ({screening_result}). "
                f"Important contributing factors include {factor_phrase}."
            )
        else:
            text = (
                f"The model classified this case as {prediction_label} ({screening_result}). "
                f"At this time, the screening result is not strongly suggestive of diabetes, although {factor_phrase} should still be monitored."
            )

        if clinical_flags:
            text += f" Clinical review note: {clinical_flags[0]}"

        text += (
            " This output is intended for screening support and not as a standalone medical diagnosis."
        )

        return text

    # =========================
    # Helper Methods
    # =========================
    def _calculate_bmi(self, height_cm: float, weight_kg: float) -> float:
        height_m = float(height_cm) / 100.0
        if height_m <= 0:
            raise ValueError("Height must be greater than 0.")
        return float(weight_kg) / (height_m ** 2)

    def _is_high_waist(self, gender: str, waist: float) -> bool:
        gender = str(gender).lower()
        waist = float(waist)

        if gender == "male":
            return waist >= 90
        if gender == "female":
            return waist >= 80
        return False

    def _deduplicate(self, items: List[str]) -> List[str]:
        seen = set()
        result = []
        for item in items:
            key = item.strip().lower()
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    def _print_summary(self, result: Dict[str, Any]):
        if not self.verbose:
            return

        print("\n===== RECOMMENDATION ENGINE SUMMARY =====")
        for key, value in result.items():
            print(f"- {key}: {value}")
        print("=========================================\n")


# =========================
# Convenience function
# =========================
def generate_recommendation_bundle(
    normalized_input: Dict[str, Any],
    prediction_result: Dict[str, Any],
    verbose: bool = True,
) -> Dict[str, Any]:
    engine = RecommendationEngine(verbose=verbose)
    return engine.generate(
        normalized_input=normalized_input,
        prediction_result=prediction_result,
    )


# =========================
# Quick test
# =========================
if __name__ == "__main__":
    sample_input = {
        "gender": "male",
        "age": 45.0,
        "hypertension": 0,
        "heart_disease": 0,
        "family_history_diabetes": 1,
        "smoking_history": "never",
        "height": 170.0,
        "weight": 82.0,
        "systolic_bp": 138.0,
        "diastolic_bp": 86.0,
        "waist_circumference": 96.0,
        "blood_glucose_level": 145.0,
        "glucose_test_type": "fasting",
        "physical_activity_level": "low",
    }

    sample_prediction_result = {
        "predicted_class": 1,
        "prediction_code": "positive",
        "prediction_label": "Likely Diabetes",
        "screening_result": "Screen Positive",
        "threshold": 0.38,
    }

    result = generate_recommendation_bundle(
        normalized_input=sample_input,
        prediction_result=sample_prediction_result,
        verbose=True,
    )

    print("=== FINAL RECOMMENDATION BUNDLE ===")
    print(result)