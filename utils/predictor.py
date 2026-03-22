from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import pandas as pd

# IMPORTANT:
# These imports must exist in this module namespace because the exported
# joblib artifact refers to utils.predictor.BMIRestorationTransformer
# and related custom classes during unpickling.
from utils.input_preprocessor import (
    BMIRestorationTransformer,
    BloodGlucosePolicyATransformer,
    FeatureDropper,
)

from utils.model_loader import get_model_loader
from utils.recommendation_engine import generate_recommendation_bundle


class Predictor:
    """
    End-to-end predictor for the AI Diabetes Screening Web App.

    New flow:
    - Load exported calibrated classification pipeline
    - Use selected_threshold from deployment_config.json
    - Predict positive-class probability internally
    - Convert to binary screening result only
    - Use rule-based layer only for explanation/recommendation
    """

    def __init__(self, verbose: bool = True):
        self.loader = get_model_loader(verbose=verbose)
        self.verbose = verbose

    # =========================
    # Logging
    # =========================
    def _log(self, message: str):
        if self.verbose:
            print(f"[Predictor] {datetime.now().strftime('%H:%M:%S')} | {message}")

    # =========================
    # Main API
    # =========================
    def predict(
        self,
        model_input_df: pd.DataFrame,
        normalized_input: Dict[str, Any],
        include_recommendations: bool = True,
        include_debug_probability: bool = False,
    ) -> Dict[str, Any]:
        self._log("Starting screening prediction...")

        model_input_df = self._validate_and_align_inputs(
            model_input_df=model_input_df,
            normalized_input=normalized_input,
        )

        model = self.loader.get_model()
        threshold = float(self.loader.get_selected_threshold())

        # =========================
        # Step 1: model classification
        # =========================
        probability = self._predict_probability(model, model_input_df)
        probability = self._clip_probability(probability)
        predicted_class = 1 if probability >= threshold else 0

        prediction_code = self._map_prediction_code(predicted_class)
        prediction_label = self._map_prediction_label(predicted_class)
        screening_result = self._map_screening_result(predicted_class)

        self._log(f"Model probability: {probability:.4f}")
        self._log(f"Threshold: {threshold:.4f}")
        self._log(f"Predicted class: {predicted_class}")
        self._log(f"Prediction label: {prediction_label}")

        result: Dict[str, Any] = {
            "predicted_class": int(predicted_class),
            "prediction_code": prediction_code,
            "prediction_label": prediction_label,
            "screening_result": screening_result,
            "threshold": round(threshold, 4),
        }

        # Optional: keep probability only for debug/internal use
        if include_debug_probability:
            result["model_probability"] = round(probability, 4)

        # =========================
        # Step 2: explanation layer
        # =========================
        if include_recommendations:
            recommendation_bundle = generate_recommendation_bundle(
                normalized_input=normalized_input,
                prediction_result=result,
                verbose=self.verbose,
            )
            result.update(recommendation_bundle)

        self._log("Screening prediction completed successfully.")
        return result

    # =========================
    # Internal helpers
    # =========================
    def _validate_and_align_inputs(
        self,
        model_input_df: pd.DataFrame,
        normalized_input: Dict[str, Any],
    ) -> pd.DataFrame:
        if not isinstance(model_input_df, pd.DataFrame):
            raise TypeError("model_input_df must be a pandas DataFrame.")

        if model_input_df.empty:
            raise ValueError("model_input_df cannot be empty.")

        if not isinstance(normalized_input, dict):
            raise TypeError("normalized_input must be a dictionary.")

        selected_features = self.loader.get_selected_features()
        missing_cols = [col for col in selected_features if col not in model_input_df.columns]
        if missing_cols:
            raise ValueError(f"model_input_df missing required columns: {missing_cols}")

        return model_input_df[selected_features].copy()

    def _predict_probability(self, model, model_input_df: pd.DataFrame) -> float:
        """
        Predict positive-class probability from full exported pipeline.
        """
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(model_input_df)

            if hasattr(proba, "shape") and len(proba.shape) == 2 and proba.shape[1] >= 2:
                return float(proba[0, 1])

            if hasattr(proba, "__len__") and len(proba) > 0:
                first = proba[0]
                if isinstance(first, (list, tuple)) and len(first) >= 2:
                    return float(first[1])
                return float(first)

        raise AttributeError(
            "Loaded model does not support predict_proba(). "
            "Expected a calibrated sklearn-compatible pipeline."
        )

    def _clip_probability(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _map_prediction_code(self, predicted_class: int) -> str:
        return "positive" if int(predicted_class) == 1 else "negative"

    def _map_prediction_label(self, predicted_class: int) -> str:
        return "Likely Diabetes" if int(predicted_class) == 1 else "Unlikely Diabetes"

    def _map_screening_result(self, predicted_class: int) -> str:
        return "Screen Positive" if int(predicted_class) == 1 else "Screen Negative"


# =========================
# Convenience function
# =========================
def run_prediction(
    model_input_df: pd.DataFrame,
    normalized_input: Dict[str, Any],
    verbose: bool = True,
    include_recommendations: bool = True,
    include_debug_probability: bool = False,
) -> Dict[str, Any]:
    predictor = Predictor(verbose=verbose)
    return predictor.predict(
        model_input_df=model_input_df,
        normalized_input=normalized_input,
        include_recommendations=include_recommendations,
        include_debug_probability=include_debug_probability,
    )


# =========================
# Quick test
# =========================
if __name__ == "__main__":
    from utils.input_preprocessor import prepare_model_input

    raw_input = {
        "gender": "male",
        "age": 45,
        "hypertension": 0,
        "heart_disease": 0,
        "family_history_diabetes": 1,
        "smoking_history": "never",
        "height": 170,
        "weight": 82,
        "systolic_bp": 138,
        "diastolic_bp": 86,
        "waist_circumference": 96,
        "blood_glucose_level": 145,
        "glucose_test_type": "fasting",
        "physical_activity_level": "Low",
    }

    loader = get_model_loader(verbose=True)

    prep_result = prepare_model_input(
        raw_input=raw_input,
        selected_features=loader.get_selected_features(),
        verbose=True,
    )

    result = run_prediction(
        model_input_df=prep_result["model_input_df"],
        normalized_input=prep_result["normalized_input"],
        verbose=True,
        include_recommendations=True,
        include_debug_probability=False,
    )

    print("\n=== FINAL RESULT ===")
    for k, v in result.items():
        print(f"{k}: {v}")