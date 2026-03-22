import streamlit as st
import sys
import os

# นำเข้า Session Manager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.session_manager import save_patient_data, init_session_state

# ==========================================
# 1. ตั้งค่าหน้าเพจ และ CSS (Medical Modern)
# ==========================================
st.set_page_config(page_title="Patient Health Profile | DiaScreen AI", page_icon="📝", layout="centered")
init_session_state()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        background-color: #f0f4f8 !important;
    }

    /* ซ่อนแถบเมนู Streamlit */
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* ============ PAGE BACKGROUND ============ */
    .stApp {
        background: linear-gradient(160deg, #eaf3ff 0%, #f0f7f4 50%, #f0f4f8 100%) !important;
        min-height: 100vh;
    }

    /* ============ MAIN CONTAINER ============ */
    .block-container {
        max-width: 860px !important;
        padding: 2rem 2rem 4rem !important;
    }

    /* ============ TOP HERO BANNER ============ */
    .hero-banner {
        background: linear-gradient(135deg, #0a3d62 0%, #1a6fa3 60%, #1db980 100%);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(10, 61, 98, 0.18);
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 200px; height: 200px;
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -60px; right: 80px;
        width: 160px; height: 160px;
        background: rgba(29,185,128,0.12);
        border-radius: 50%;
    }
    .hero-eyebrow {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #7ee8bf;
        margin-bottom: 0.4rem;
    }
    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: #ffffff;
        margin: 0 0 0.4rem 0;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 0.92rem;
        color: rgba(255,255,255,0.72);
        margin: 0;
        max-width: 480px;
    }
    .hero-badge {
        position: absolute;
        top: 1.5rem; right: 2rem;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 40px;
        padding: 0.35rem 1rem;
        font-size: 0.78rem;
        color: rgba(255,255,255,0.9);
        font-weight: 500;
        backdrop-filter: blur(4px);
    }

    /* ============ PROGRESS BAR ============ */
    .progress-wrap {
        background: #ffffff;
        border-radius: 14px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.8rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        border: 1px solid #e2ecf5;
    }
    .step-dot {
        width: 28px; height: 28px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.72rem;
        font-weight: 700;
        flex-shrink: 0;
    }
    .step-dot.active {
        background: #1a6fa3; color: #fff;
    }
    .step-dot.done {
        background: #1db980; color: #fff;
    }
    .step-dot.pending {
        background: #e8edf2; color: #94a3b8;
    }
    .step-line {
        flex: 1; height: 2px;
        background: #e8edf2;
        border-radius: 2px;
    }
    .step-label {
        font-size: 0.72rem;
        color: #64748b;
        font-weight: 500;
        white-space: nowrap;
    }

    /* ============ CARD SECTIONS ============ */
    .card-section {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.6rem 1.8rem 1.2rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.05);
        border: 1px solid #e2ecf5;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 1.25rem;
        padding-bottom: 0.8rem;
        border-bottom: 1.5px solid #eef3f9;
    }
    .section-icon-wrap {
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem;
        flex-shrink: 0;
    }
    .section-icon-wrap.blue  { background: #e8f1fb; }
    .section-icon-wrap.green { background: #e4f7ef; }
    .section-icon-wrap.amber { background: #fef3e2; }
    .section-title {
        font-size: 0.97rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
        letter-spacing: -0.01em;
    }
    .section-desc {
        font-size: 0.78rem;
        color: #94a3b8;
        margin: 0;
        font-weight: 400;
    }

    /* ============ FIELD LABELS ============ */
    label, .stSelectbox label, .stNumberInput label, .stTextInput label {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        letter-spacing: 0.01em !important;
        margin-bottom: 0.3rem !important;
    }

    /* ============ INPUTS ============ */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        border-color: #dde6f0 !important;
        background: #f8fafc !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #1a6fa3 !important;
        box-shadow: 0 0 0 3px rgba(26,111,163,0.1) !important;
    }

    /* ============ BMI CHIP ============ */
    .bmi-chip {
        background: linear-gradient(135deg, #e8f7f1, #d4f0e7);
        border: 1px solid #a7e3cc;
        border-radius: 10px;
        padding: 0.55rem 1rem;
        text-align: center;
        margin-top: 1.72rem;
    }
    .bmi-label { font-size: 0.7rem; color: #0f7a55; font-weight: 600; letter-spacing: 0.08em; }
    .bmi-value { font-size: 1.5rem; font-weight: 700; color: #0a5c40; line-height: 1.1; }

    /* ============ INFO PILLS ============ */
    .info-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: #f0f7ff;
        border: 1px solid #c6ddf5;
        border-radius: 30px;
        padding: 0.3rem 0.85rem;
        font-size: 0.76rem;
        color: #1a6fa3;
        font-weight: 500;
        margin-bottom: 1rem;
    }

    /* ============ BACK BUTTON ============ */
    div.stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 1.5px solid #dde6f0 !important;
        color: #64748b !important;
        border-radius: 10px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.2s !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #1a6fa3 !important;
        color: #1a6fa3 !important;
        background: #f0f7ff !important;
    }

    /* ============ SUBMIT BUTTON ============ */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0a3d62 0%, #1a6fa3 60%, #1db980 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        padding: 0.85rem 2rem !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        letter-spacing: -0.01em !important;
        transition: all 0.25s !important;
        box-shadow: 0 6px 20px rgba(10, 61, 98, 0.25) !important;
        width: 100% !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 28px rgba(10, 61, 98, 0.32) !important;
        filter: brightness(1.05) !important;
    }
    div.stButton > button:first-child:active {
        transform: translateY(0) !important;
    }

    /* ============ DIVIDER ============ */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2ecf5, transparent);
        margin: 0.5rem 0 1.2rem;
    }

    /* ============ FOOTER NOTE ============ */
    .footer-note {
        text-align: center;
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #e8edf4;
    }
    .footer-note strong { color: #64748b; }

    /* ============ ERROR ============ */
    .stAlert { border-radius: 12px !important; }

    </style>
""", unsafe_allow_html=True)

# ==========================================
# Helper Functions (ไม่แตะ logic)
# ==========================================
def normalize_physical_activity(value: str) -> str:
    mapping = {"Low": "low", "Moderate": "moderate", "High": "high"}
    return mapping.get(value, value)

def normalize_smoking_history(value: str) -> str:
    mapping = {
        "No Info": "no info", "never": "never", "former": "former",
        "not current": "not current", "current": "current", "ever": "ever",
    }
    return mapping.get(value, value)

def clear_previous_prediction_state():
    keys_to_clear = [
        "prediction_result", "api_response", "api_error",
        "risk_result", "recommendation_bundle", "processing_error",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

# ==========================================
# HERO BANNER
# ==========================================
st.markdown("""
<div class="hero-banner">
    <div class="hero-eyebrow">🩺 DiaScreen AI - Diabetes Screening</div>
    <h1 class="hero-title">Patient Health Profile</h1>
    <p class="hero-sub">Complete the health and lifestyle questionnaire below to receive a simple diabetes screening result and helpful recommendations.</p>
    <div class="hero-badge">⚡ Powered by AI · Instant Results</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# PROGRESS INDICATOR
# ==========================================
st.markdown("""
<div class="progress-wrap">
    <div class="step-dot active">1</div>
    <span class="step-label" style="color:#1a6fa3;font-weight:600">Health Profile</span>
    <div class="step-line"></div>
    <div class="step-dot pending">2</div>
    <span class="step-label">AI Analysis</span>
    <div class="step-line"></div>
    <div class="step-dot pending">3</div>
    <span class="step-label">Results & Advice</span>
</div>
""", unsafe_allow_html=True)

# Back button
col_back, _ = st.columns([0.13, 0.87])
with col_back:
    if st.button("← Back", help="Back to Home"):
        st.switch_page("app.py")

# ==========================================
# SECTION 1 — Demographics & Body Metrics
# ==========================================
st.markdown("""
<div class="card-section">
    <div class="section-header">
        <div class="section-icon-wrap blue">👤</div>
        <div>
            <p class="section-title">Demographics & Body Metrics</p>
            <p class="section-desc">Basic personal and anthropometric data</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="card-section" style="margin-top:-1rem">', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        gender = st.selectbox("Gender", ["Select", "male", "female"])
    with c2:
        age = st.number_input("Age (Years)", min_value=1, max_value=120, value=45, step=1)
    with c3:
        waist_circumference = st.number_input("Waist Circumference (cm)", min_value=30.0, max_value=200.0, value=85.0, step=0.1)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
    with c5:
        weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0, step=0.1)
    with c6:
        calculated_bmi = 0.0
        if height > 0 and weight > 0:
            calculated_bmi = weight / ((height / 100) ** 2)

        # Classify BMI
        if calculated_bmi < 18.5:
            bmi_status = "Underweight"
        elif calculated_bmi < 25:
            bmi_status = "Normal"
        elif calculated_bmi < 30:
            bmi_status = "Overweight"
        else:
            bmi_status = "Obese"

        st.markdown(f"""
        <div style="margin-top:0.25rem">
            <div style="font-size:0.8rem;font-weight:600;color:#475569;margin-bottom:0.4rem">BMI (Auto-calculated)</div>
            <div class="bmi-chip">
                <div class="bmi-value">{calculated_bmi:.1f}</div>
                <div class="bmi-label">{bmi_status}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECTION 2 — Clinical History & Vitals
# ==========================================
with st.container():
    st.markdown("""
    <div class="section-header" style="margin-top:0.5rem">
        <div class="section-icon-wrap green">🩺</div>
        <div>
            <p class="section-title">Clinical History & Vitals</p>
            <p class="section-desc">Blood glucose, blood pressure, and medical history</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card-section" style="margin-top:-0.5rem">', unsafe_allow_html=True)

    c7, c8, c9 = st.columns(3)
    with c7:
        glucose_test_type = st.selectbox("Glucose Test Type", ["Select", "fasting", "random"])
    with c8:
        blood_glucose_level = st.number_input("Glucose Level (mg/dL)", min_value=30.0, max_value=500.0, value=105.0, step=1.0)
    with c9:
        systolic_bp = st.number_input("Systolic BP (mmHg)", min_value=70, max_value=250, value=120, step=1)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    c10, c11, c12 = st.columns(3)
    with c10:
        diastolic_bp = st.number_input("Diastolic BP (mmHg)", min_value=40, max_value=150, value=80, step=1)
    with c11:
        hypertension = st.selectbox("Hypertension History", ["Select", "Yes", "No"])
    with c12:
        heart_disease = st.selectbox("Heart Disease History", ["Select", "Yes", "No"])

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    c13, _, _ = st.columns(3)
    with c13:
        family_history_diabetes = st.selectbox("Family History of Diabetes", ["Select", "Yes", "No"])

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SECTION 3 — Lifestyle Factors
# ==========================================
with st.container():
    st.markdown("""
    <div class="section-header" style="margin-top:0.5rem">
        <div class="section-icon-wrap amber">🏃</div>
        <div>
            <p class="section-title">Lifestyle Factors</p>
            <p class="section-desc">Smoking behavior and physical activity patterns</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card-section" style="margin-top:-0.5rem">', unsafe_allow_html=True)

    c14, c15, _ = st.columns(3)
    with c14:
        smoking = st.selectbox("Smoking History", ["Select", "never", "former", "not current", "current", "ever", "No Info"])
    with c15:
        physical_activity_level = st.selectbox("Physical Activity Level", ["Select", "Low", "Moderate", "High"])

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SUBMIT BUTTON & VALIDATION (ไม่แตะ logic)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;margin-bottom:0.75rem">
    <span class="info-pill">🔒 Your data is processed securely and not stored permanently</span>
</div>
""", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    if st.button("🧠  Run AI Risk Assessment", use_container_width=True):
        required_fields = [
            gender,
            glucose_test_type,
            hypertension,
            heart_disease,
            family_history_diabetes,
            smoking,
            physical_activity_level
        ]

        if "Select" in required_fields:
            st.error("⚠️ Please fill in all required dropdown fields (Gender, Glucose Test Type, etc.) before running the assessment.")
        else:
            map_yn = {"Yes": 1, "No": 0}

            # API-ready payload (ไม่แตะ)
            patient_data = {
                "gender": gender,
                "age": float(age),
                "hypertension": int(map_yn[hypertension]),
                "heart_disease": int(map_yn[heart_disease]),
                "family_history_diabetes": int(map_yn[family_history_diabetes]),
                "smoking_history": normalize_smoking_history(smoking),
                "height": float(height),
                "weight": float(weight),
                "bmi": round(calculated_bmi, 1),
                "systolic_bp": float(systolic_bp),
                "diastolic_bp": float(diastolic_bp),
                "waist_circumference": float(waist_circumference),
                "blood_glucose_level": float(blood_glucose_level),
                "glucose_test_type": glucose_test_type,
                "physical_activity_level": normalize_physical_activity(physical_activity_level),
            }

            clear_previous_prediction_state()
            save_patient_data(patient_data)
            st.session_state["api_payload"] = patient_data
            st.session_state["ready_for_api"] = True

            try:
                st.switch_page("pages/2_AI_Processing.py")
            except Exception:
                st.error("⚠️ ไม่พบไฟล์ `pages/2_AI_Processing.py`")

st.markdown("""
<div class="footer-note">
    DiaScreen AI · For screening purposes only · <strong>Not a medical diagnosis</strong><br>
    Always consult a licensed healthcare professional for clinical decisions.
</div>
""", unsafe_allow_html=True)