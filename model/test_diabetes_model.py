import json
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from pathlib import Path

# =========================
# 1) Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "xgboost_diabetes_model.json"
METADATA_PATH = BASE_DIR / "xgboost_diabetes_model_metadata.json"
PREPROCESSOR_PATH = BASE_DIR / "xgboost_preprocessor.pkl"


# =========================
# 2) Helper: load metadata
# =========================
def load_metadata(metadata_path: Path) -> dict:
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return metadata


# =========================
# 3) Helper: load xgboost booster
# =========================
def load_xgb_booster(model_path: Path) -> xgb.Booster:
    booster = xgb.Booster()
    booster.load_model(str(model_path))
    return booster


# =========================
# 4) Helper: load preprocessor
# =========================
def load_preprocessor(preprocessor_path: Path):
    return joblib.load(preprocessor_path)


# =========================
# 5) Build one test sample
# IMPORTANT:
# - ต้องใช้ชื่อ feature ให้ตรงกับ metadata
# - blood_glucose_level_log ต้องเป็นค่าที่ผ่าน log มาแล้ว
# - bmi_recalculated ต้องเป็นค่าที่คำนวณแล้ว
# =========================
def build_test_input() -> pd.DataFrame:
    sample = {
        "gender": "female",
        "smoking_history": "never",
        "physical_activity_level": "low",
        "hypertension": 1,
        "heart_disease": 0,
        "family_history_diabetes": 1,
        "age": 55,
        "bmi_recalculated": 28.4,
        "blood_glucose_level_log": np.log1p(145),   # example: raw glucose = 145
        "height": 158,
        "weight": 75,
        "waist_circumference": 88,
        "systolic_bp": 138.0,
        "diastolic_bp": 88.0
    }

    return pd.DataFrame([sample])


# =========================
# 6) Prediction function
# =========================
def predict_one():
    print("=== Loading metadata ===")
    metadata = load_metadata(METADATA_PATH)
    print("Model name:", metadata.get("model_name"))
    print("Selected features:", metadata.get("selected_features"))

    print("\n=== Loading preprocessor ===")
    preprocessor = load_preprocessor(PREPROCESSOR_PATH)
    print("Preprocessor loaded successfully.")

    print("\n=== Loading XGBoost model ===")
    booster = load_xgb_booster(MODEL_PATH)
    print("Model loaded successfully.")

    print("\n=== Building test input ===")
    X_input = build_test_input()

    # Ensure column order matches metadata
    selected_features = metadata["selected_features"]
    X_input = X_input[selected_features]

    print(X_input)

    print("\n=== Transform input ===")
    X_processed = preprocessor.transform(X_input)

    print("Processed shape:", X_processed.shape)

    print("\n=== Predict ===")
    dmatrix = xgb.DMatrix(X_processed)

    prob = booster.predict(dmatrix)[0]

    # Default binary threshold
    pred = 1 if prob >= 0.5 else 0

    print(f"Predicted probability of diabetes: {prob:.4f}")
    print(f"Predicted class: {pred} ({'Diabetes Risk' if pred == 1 else 'No Diabetes Risk'})")


if __name__ == "__main__":
    try:
        predict_one()
    except Exception as e:
        print("\n[ERROR]")
        print(type(e).__name__, ":", e)
        print(
            "\nHint:\n"
            "- ถ้า error ตอน load preprocessor.pkl ให้เช็ก scikit-learn version\n"
            "- แนะนำใช้ version เดียวกับตอน export จาก Colab\n"
        )