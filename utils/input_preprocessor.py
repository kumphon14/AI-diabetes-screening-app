import math
from datetime import datetime
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


class InputPreprocessor:
    """
    Preprocess raw input from UI/API into model-ready input.

    Responsibilities:
    1. Validate required fields
    2. Normalize categorical values
    3. Compute engineered features required by exported model:
       - bmi
       - blood_glucose_level_log
    4. Align output fields with model selected_features
    5. Return:
       - normalized_input
       - model_input_df
    """

    def __init__(self, selected_features: List[str], verbose: bool = True):
        self.selected_features = selected_features
        self.verbose = verbose

        self.allowed_gender = {"male", "female"}
        self.allowed_smoking_history = {
            "never",
            "former",
            "not current",
            "current",
            "ever",
            "no info",
        }
        self.allowed_physical_activity = {"low", "moderate", "high"}
        self.allowed_glucose_test_type = {"fasting", "random"}

        self.required_raw_fields = {
            "gender",
            "age",
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

    # =========================
    # Logging
    # =========================
    def _log(self, message: str):
        if self.verbose:
            print(
                f"[InputPreprocessor] {datetime.now().strftime('%H:%M:%S')} | {message}"
            )

    # =========================
    # Public API
    # =========================
    def preprocess(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entrypoint.

        Returns:
            {
                "normalized_input": dict,
                "model_input_df": pandas.DataFrame
            }
        """
        self._log("Starting input preprocessing...")

        if not isinstance(raw_input, dict):
            raise TypeError("raw_input must be a dictionary.")

        self._validate_required_fields(raw_input)

        normalized = self._normalize_input(raw_input)
        self._validate_ranges(normalized)

        model_payload = self._build_model_payload(normalized)
        self._validate_selected_features(model_payload)

        df = pd.DataFrame([model_payload], columns=self.selected_features)

        self._log("Preprocessing completed successfully.")
        self._print_summary(normalized, model_payload, df)

        return {
            "normalized_input": normalized,
            "model_input_df": df,
        }

    # =========================
    # Validation
    # =========================
    def _validate_required_fields(self, raw_input: Dict[str, Any]):
        missing = [field for field in self.required_raw_fields if field not in raw_input]
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")
        self._log("Required field validation passed.")

    def _validate_ranges(self, data: Dict[str, Any]):
        """
        Validate numeric ranges for safety and plausibility.
        These are sanity checks, not diagnosis rules.
        """
        self._assert_range(data["age"], "age", 1, 120)
        self._assert_range(data["height"], "height", 50, 250)
        self._assert_range(data["weight"], "weight", 10, 300)
        self._assert_range(data["systolic_bp"], "systolic_bp", 70, 250)
        self._assert_range(data["diastolic_bp"], "diastolic_bp", 40, 150)
        self._assert_range(data["waist_circumference"], "waist_circumference", 30, 200)
        self._assert_range(data["blood_glucose_level"], "blood_glucose_level", 30, 500)

        if data["diastolic_bp"] >= data["systolic_bp"]:
            raise ValueError(
                "Invalid blood pressure values: diastolic_bp must be lower than systolic_bp."
            )

        if data["hypertension"] not in (0, 1):
            raise ValueError("hypertension must be 0 or 1.")

        if data["heart_disease"] not in (0, 1):
            raise ValueError("heart_disease must be 0 or 1.")

        if data["family_history_diabetes"] not in (0, 1):
            raise ValueError("family_history_diabetes must be 0 or 1.")

        self._log("Range and logical validation passed.")

    def _assert_range(
        self,
        value: Any,
        field_name: str,
        min_value: float,
        max_value: float,
    ):
        if value is None:
            raise ValueError(f"{field_name} cannot be null.")

        if isinstance(value, float) and math.isnan(value):
            raise ValueError(f"{field_name} cannot be NaN.")

        if not (min_value <= float(value) <= max_value):
            raise ValueError(
                f"{field_name} out of range: {value}. Expected between {min_value} and {max_value}."
            )

    # =========================
    # Normalization
    # =========================
    def _normalize_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize incoming UI/API values into a consistent internal format.
        """
        data = dict(raw_input)

        # strings
        data["gender"] = self._normalize_gender(data.get("gender"))
        data["smoking_history"] = self._normalize_smoking_history(
            data.get("smoking_history")
        )
        data["physical_activity_level"] = self._normalize_physical_activity(
            data.get("physical_activity_level")
        )

        # optional
        if "glucose_test_type" in data and data["glucose_test_type"] not in (None, ""):
            data["glucose_test_type"] = self._normalize_glucose_test_type(
                data["glucose_test_type"]
            )

        # numerics
        numeric_fields = [
            "age",
            "height",
            "weight",
            "systolic_bp",
            "diastolic_bp",
            "waist_circumference",
            "blood_glucose_level",
        ]
        for field in numeric_fields:
            data[field] = float(data[field])

        # binary flags -> int
        data["hypertension"] = self._normalize_binary_flag(
            data.get("hypertension"),
            "hypertension",
        )
        data["heart_disease"] = self._normalize_binary_flag(
            data.get("heart_disease"),
            "heart_disease",
        )
        data["family_history_diabetes"] = self._normalize_binary_flag(
            data.get("family_history_diabetes"),
            "family_history_diabetes",
        )

        # optional bmi from UI
        if "bmi" in data and data["bmi"] not in (None, ""):
            try:
                data["bmi"] = float(data["bmi"])
            except (TypeError, ValueError):
                data["bmi"] = None

        self._log("Input normalization completed.")
        return data

    def _normalize_gender(self, value: Any) -> str:
        if value is None:
            raise ValueError("gender is required.")

        v = str(value).strip().lower()
        mapping = {
            "male": "male",
            "m": "male",
            "female": "female",
            "f": "female",
        }
        v = mapping.get(v, v)

        if v not in self.allowed_gender:
            raise ValueError(
                f"Invalid gender: {value}. Allowed: {sorted(self.allowed_gender)}"
            )
        return v

    def _normalize_smoking_history(self, value: Any) -> str:
        if value is None:
            raise ValueError("smoking_history is required.")

        v = str(value).strip().lower()
        mapping = {
            "no info": "no info",
            "no_info": "no info",
            "not_current": "not current",
        }
        v = mapping.get(v, v)

        if v not in self.allowed_smoking_history:
            raise ValueError(
                f"Invalid smoking_history: {value}. Allowed: {sorted(self.allowed_smoking_history)}"
            )
        return v

    def _normalize_physical_activity(self, value: Any) -> str:
        if value is None:
            raise ValueError("physical_activity_level is required.")

        v = str(value).strip().lower()
        if v not in self.allowed_physical_activity:
            raise ValueError(
                f"Invalid physical_activity_level: {value}. "
                f"Allowed: {sorted(self.allowed_physical_activity)}"
            )
        return v

    def _normalize_glucose_test_type(self, value: Any) -> str:
        v = str(value).strip().lower()
        if v not in self.allowed_glucose_test_type:
            raise ValueError(
                f"Invalid glucose_test_type: {value}. Allowed: {sorted(self.allowed_glucose_test_type)}"
            )
        return v

    def _normalize_binary_flag(self, value: Any, field_name: str) -> int:
        true_values = {1, "1", True, "true", "yes", "y"}
        false_values = {0, "0", False, "false", "no", "n"}

        if value in true_values:
            return 1
        if value in false_values:
            return 0

        raise ValueError(
            f"Invalid {field_name}: {value}. Expected one of 0/1, yes/no, true/false."
        )

    # =========================
    # Feature engineering
    # =========================
    def _build_model_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build payload exactly matching exported selected_features.

        Based on deployment config:
        - bmi is required
        - blood_glucose_level_log is required
        """
        height_m = data["height"] / 100.0
        bmi_value = data["weight"] / (height_m ** 2)
        blood_glucose_level_log = float(np.log1p(data["blood_glucose_level"]))

        model_payload = {
            "gender": data["gender"],
            "smoking_history": data["smoking_history"],
            "physical_activity_level": data["physical_activity_level"],
            "hypertension": int(data["hypertension"]),
            "heart_disease": int(data["heart_disease"]),
            "family_history_diabetes": int(data["family_history_diabetes"]),
            "age": float(data["age"]),
            "bmi": float(round(bmi_value, 4)),
            "blood_glucose_level_log": float(round(blood_glucose_level_log, 6)),
            "height": float(data["height"]),
            "weight": float(data["weight"]),
            "waist_circumference": float(data["waist_circumference"]),
            "systolic_bp": float(data["systolic_bp"]),
            "diastolic_bp": float(data["diastolic_bp"]),
        }

        self._log("Feature engineering completed.")
        return model_payload

    def _validate_selected_features(self, model_payload: Dict[str, Any]):
        missing = [f for f in self.selected_features if f not in model_payload]
        extras = [f for f in model_payload if f not in self.selected_features]

        if missing:
            raise ValueError(f"Model payload missing selected features: {missing}")

        if extras:
            self._log(f"Extra payload fields not used by model: {extras}")

        self._log("Selected feature alignment passed.")

    # =========================
    # Debug helpers
    # =========================
    def debug_raw_input(self, raw_input: Dict[str, Any]):
        print("\n=== RAW INPUT DEBUG ===")
        for k, v in raw_input.items():
            print(f"{k}: {v}")
        print("=======================\n")

    def debug_selected_features(self):
        print("\n=== SELECTED FEATURES DEBUG ===")
        for i, f in enumerate(self.selected_features, start=1):
            print(f"{i:2d}. {f}")
        print("================================\n")

    def _print_summary(
        self,
        normalized: Dict[str, Any],
        model_payload: Dict[str, Any],
        df: pd.DataFrame,
    ):
        if not self.verbose:
            return

        print("\n========== INPUT PREPROCESSOR SUMMARY ==========")
        print("Normalized input:")
        for k, v in normalized.items():
            print(f"- {k}: {v}")

        print("\nModel payload:")
        for k, v in model_payload.items():
            print(f"- {k}: {v}")

        print("\nFinal DataFrame shape:", df.shape)
        print("Final DataFrame columns:", list(df.columns))
        print("================================================\n")


# =========================
# Convenience function
# =========================
def prepare_model_input(
    raw_input: Dict[str, Any],
    selected_features: List[str],
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function for one-shot preprocessing.

    Returns:
        {
            "normalized_input": dict,
            "model_input_df": pandas.DataFrame
        }
    """
    processor = InputPreprocessor(
        selected_features=selected_features,
        verbose=verbose,
    )
    return processor.preprocess(raw_input)


class BMIRestorationTransformer(BaseEstimator, TransformerMixin):
    """
    Restore / recompute BMI from height and weight.
    The exported model expects this class to exist at load time.
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()

        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)

        if "height" in df.columns and "weight" in df.columns:
            height_m = pd.to_numeric(df["height"], errors="coerce") / 100.0
            weight_kg = pd.to_numeric(df["weight"], errors="coerce")
            bmi = weight_kg / (height_m ** 2)
            bmi = bmi.replace([np.inf, -np.inf], np.nan)

            df["bmi"] = bmi

        return df


class BloodGlucosePolicyATransformer(BaseEstimator, TransformerMixin):
    """
    Create blood_glucose_level_log from blood_glucose_level.
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()

        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)

        if "blood_glucose_level" in df.columns:
            glucose = pd.to_numeric(df["blood_glucose_level"], errors="coerce").clip(lower=0)
            df["blood_glucose_level_log"] = np.log1p(glucose)

        return df


class FeatureDropper(BaseEstimator, TransformerMixin):
    """
    Drop selected columns if present.
    The exported model expects this class to exist at load time.
    """

    def __init__(self, columns_to_drop=None):
        self.columns_to_drop = columns_to_drop or []

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()

        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)

        cols = [col for col in self.columns_to_drop if col in df.columns]
        if cols:
            df = df.drop(columns=cols)

        return df