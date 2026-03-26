# 🩺 DiaScreen AI  
### AI-Powered Diabetes Screening Web Application

<img width="963" height="499" alt="image" src="https://github.com/user-attachments/assets/759cfc94-cdee-4a1c-9f7a-ae008cc5d700" />

AI Diabetes Screening App is a Streamlit + FastAPI project for diabetes screening classification using a machine learning model together with a rule-based clinical explanation layer.

🧑‍⚕️ The system is designed to:
- classify screening results as `Likely Diabetes` or `Unlikely Diabetes`
- provide `Screen Positive` or `Screen Negative`
- generate `Clinical Flags`
- identify `Key Risk Factors`
- generate `Recommendations`
- display a clear screening summary in a Streamlit web application

<p align="center">
  <img alt="Streamlit" src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="Render" src="https://img.shields.io/badge/Deployment-Render-4A90E2?style=for-the-badge">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="ML" src="https://img.shields.io/badge/Machine%20Learning-Classification-6A5ACD?style=for-the-badge">
</p>

<p align="center">
  <b>DiaScreen AI</b> is a web-based diabetes screening system that combines a <b>machine learning classification model</b> with a <b>rule-based clinical explanation layer</b> to provide an accessible, interpretable, and user-friendly health screening experience.
</p>

---

## 📌 Project Overview

DiaScreen AI is designed to support **preliminary diabetes risk screening** through a modern web application workflow.

The system allows users to:

- enter personal and health-related information,
- send structured data to an AI screening API,
- receive a prediction result,
- and view an interpretable summary including:
  - **screening result**
  - **key risk factors**
  - **clinical flags**
  - **recommendations**
  - **short interpretation**

> ⚠️ This system is intended for **screening support only** and **must not be used as a medical diagnosis tool**.

---

## ✨ Key Features

### 1) Interactive Web-Based Screening
Users can input health-related information through a responsive Streamlit interface.

### 2) AI-Based Diabetes Classification
The backend processes structured health data and performs diabetes screening using a deployed machine learning model.

### 3) Rule-Based Clinical Explanation Layer
In addition to prediction, the system generates human-readable outputs such as:
- Key Risk Factors
- Clinical Flags
- Recommendations
- Short Interpretation

### 4) Multi-Page User Flow
The application is organized into a clear 3-step journey:

- **Step 1:** Health Data Input  
- **Step 2:** AI Processing  
- **Step 3:** Risk Analysis Result  

### 5) API Health Monitoring
The backend provides service monitoring endpoints:
- `/health`
- `/model/health`
- `/predict`

### 6) Session-Based Workflow Management
The system preserves patient input, API payload, prediction result, and processing state using Streamlit session state.

---

## 🧠 System Architecture

```text
User
  ↓
Streamlit Web App
  ├── 1_Health_Data_Input.py
  ├── 2_AI_Processing.py
  └── 3_AI_Risk_Analysis_Result.py
  ↓
FastAPI Backend
  ├── /health
  ├── /model/health
  └── /predict
  ↓
ML Model + Input Preprocessing + Rule-Based Explanation
  ↓
Prediction Result + Clinical Summary

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
