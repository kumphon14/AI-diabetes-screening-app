import json
import joblib
import xgboost as xgb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "xgboost_diabetes_model.json"
METADATA_PATH = BASE_DIR / "xgboost_diabetes_model_metadata.json"
PREPROCESSOR_PATH = BASE_DIR / "xgboost_preprocessor.pkl"

print("=== CHECK FILES ===")

# 1) metadata
try:
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print("[OK] Metadata loaded")
    print("Model name:", metadata.get("model_name"))
except Exception as e:
    print("[FAIL] Metadata:", e)

# 2) xgboost model
try:
    booster = xgb.Booster()
    booster.load_model(str(MODEL_PATH))
    print("[OK] XGBoost model loaded")
except Exception as e:
    print("[FAIL] XGBoost model:", e)

# 3) preprocessor
try:
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    print("[OK] Preprocessor loaded")
    print("Type:", type(preprocessor))
except Exception as e:
    print("[FAIL] Preprocessor:", e)