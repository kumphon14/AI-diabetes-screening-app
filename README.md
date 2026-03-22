# 🧑‍⚕️ AI Diabetes Screening App

AI Diabetes Screening App is a Streamlit + FastAPI project for diabetes screening classification using a machine learning model together with a rule-based clinical explanation layer.

The system is designed to:
- classify screening results as `Likely Diabetes` or `Unlikely Diabetes`
- provide `Screen Positive` or `Screen Negative`
- generate `Clinical Flags`
- identify `Key Risk Factors`
- generate `Recommendations`
- display a clear screening summary in a Streamlit web application

---

## 📂 Project Structure

```text
AI_DIABETES_RISK_APP/
├── .streamlit/
├── assets/
├── model/
│   ├── best_pipeline.joblib
│   ├── calibrated_model.joblib
│   ├── check_export_files.py
│   ├── deployment_config.json
│   └── test_diabetes_model.py
├── pages/
│   ├── 1_Health_Data_Input.py
│   ├── 2_AI_Processing.py
│   └── 3_AI_Risk_Analysis_Result.py
├── utils/
│   ├── __init__.py
│   ├── input_preprocessor.py
│   ├── model_loader.py
│   ├── predictor.py
│   ├── recommendation_engine.py
│   └── session_manager.py
├── api.py
├── app.py
├── requirements.txt
├── test_api.py
├── test_cases.json
└── README.md
```

## ✅ Features App
Streamlit multipage frontend
FastAPI backend API
ML-based diabetes screening classification
Rule-based clinical explanation layer
Clinical flags and recommendations
Local API testing with mock JSON cases
Clear separation between prediction and explanation logic

## Tech Stack
Python
Streamlit
FastAPI
Uvicorn
Pandas
NumPy
Scikit-learn
Joblib
XGBoost
Requests
Pydantic

## 💭 Setup
1) Create virtual environment
Windows
```text
python -m venv venv
venv\Scripts\activate
```

macOS / Linux
```text
python3 -m venv venv
source venv/bin/activate
```

2) Install dependencies
```text
pip install -r requirements.txt
```

## Run the Project
###  ▶️ Run FastAPI backend
```text
uvicorn api:app --reload

FastAPI runs at:

http://127.0.0.1:8000

Swagger docs:

http://127.0.0.1:8000/docs
```

### ▶️ Run Streamlit frontend
```text
Open another terminal and run:

streamlit run app.py
API Endpoints
GET /health

Basic API health check.

GET /model/health

Model and config health check.

POST /predict

Run diabetes screening classification and return explanation output.

Example request:

{
  "gender": "male",
  "age": 47,
  "hypertension": 0,
  "heart_disease": 0,
  "family_history_diabetes": 1,
  "smoking_history": "former",
  "height": 170,
  "weight": 82,
  "systolic_bp": 132,
  "diastolic_bp": 84,
  "waist_circumference": 94,
  "blood_glucose_level": 112,
  "glucose_test_type": "fasting",
  "physical_activity_level": "low"
}

Example response:

{
  "status": "success",
  "data": {
    "predicted_class": 0,
    "prediction_code": "negative",
    "prediction_label": "Unlikely Diabetes",
    "screening_result": "Screen Negative",
    "clinical_flags": [
      "Fasting blood glucose is in the prediabetes range (100-125 mg/dL)."
    ],
    "key_risk_factors": [
      "Fasting glucose in prediabetes range",
      "Age 45 years or older",
      "Family history of diabetes"
    ],
    "recommendations": [
      "Current screening does not strongly suggest diabetes, but ongoing preventive monitoring is still recommended."
    ],
    "short_interpretation": "This screening result does not strongly suggest diabetes at this time, but some risk factors should still be monitored."
  }
}
```

## Testing
Run local API test

Make sure FastAPI is already running, then execute:
```text
python test_api.py
```

### Test cases
```test_cases.json```
can store grouped mock cases such as:
- positive_cases
- negative_cases
