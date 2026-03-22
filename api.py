from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

# ====== Your modules ======
from utils.model_loader import get_model_loader
from utils.input_preprocessor import prepare_model_input
from utils.predictor import Predictor


# =========================
# FastAPI App
# =========================
app = FastAPI(
    title="AI Diabetes Screening API",
    version="2.1.0",
    description="ML-based diabetes screening classification API with rule-based clinical explanation"
)

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Load model once
# =========================
loader = get_model_loader(verbose=False)
predictor = Predictor(verbose=False)


# =========================
# Request Schema
# =========================
class PredictRequest(BaseModel):
    gender: Literal["male", "female"]
    age: float = Field(..., ge=1, le=120)

    hypertension: Literal[0, 1]
    heart_disease: Literal[0, 1]
    family_history_diabetes: int

    smoking_history: str

    height: float = Field(..., ge=50, le=250)
    weight: float = Field(..., ge=10, le=300)

    systolic_bp: float = Field(..., ge=70, le=250)
    diastolic_bp: float = Field(..., ge=40, le=150)

    waist_circumference: float = Field(..., ge=30, le=200)

    blood_glucose_level: float = Field(..., ge=30, le=500)
    glucose_test_type: Literal["fasting", "random"]

    physical_activity_level: str

    @field_validator("family_history_diabetes", mode="before")
    @classmethod
    def validate_family_history_diabetes(cls, v):
        if v in (0, 1, "0", "1"):
            return int(v)
        raise ValueError("family_history_diabetes must be 0 or 1")

    @field_validator("smoking_history", "physical_activity_level", mode="before")
    @classmethod
    def normalize_strings(cls, v):
        if v is None:
            return v
        return str(v).strip().lower()


# =========================
# Response Schema
# =========================
class PredictResponse(BaseModel):
    status: str
    data: Dict[str, Any]


# =========================
# Health Check
# =========================
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "API is running"
    }


# =========================
# Model Health Check
# =========================
@app.get("/model/health")
def model_health():
    try:
        return {
            "status": "ok",
            "model": loader.health_check(),
            "selected_features": loader.get_selected_features(),
            "threshold": loader.get_selected_threshold(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model health check failed: {str(e)}")


# =========================
# Main Endpoint
# =========================
@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(request: PredictRequest):
    try:
        # 1) Convert request -> dict
        raw_input = request.model_dump()

        # 2) Preprocessing
        prep_result = prepare_model_input(
            raw_input=raw_input,
            selected_features=loader.get_selected_features(),
            verbose=False
        )

        model_df = prep_result["model_input_df"]
        normalized_input = prep_result["normalized_input"]

        # 3) Classification + explanation
        final_output = predictor.predict(
            model_input_df=model_df,
            normalized_input=normalized_input,
            include_recommendations=True,
            include_debug_probability=False,
        )

        return {
            "status": "success",
            "data": final_output
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )