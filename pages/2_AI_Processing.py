import os
import sys
import time
import requests
import streamlit as st

# ==========================================
# Import utilities
# ==========================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.session_manager import (
    get_patient_data,
    save_risk_result,
    init_session_state,
    save_api_response,
)

# ==========================================
# API Config
# ==========================================
API_BASE_URL = "http://127.0.0.1:8000"
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
API_TIMEOUT_SECONDS = 30

# ==========================================
# Page config
# ==========================================
st.set_page_config(
    page_title="AI Processing | DiaScreen AI",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

init_session_state()

# ==========================================
# Custom CSS — matches Page 1 design system
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        background-color: #f0f4f8 !important;
    }

    [data-testid="collapsedControl"] {display: none;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── PAGE BACKGROUND ── */
    .stApp {
        background: linear-gradient(160deg, #eaf3ff 0%, #f0f7f4 50%, #f0f4f8 100%) !important;
        min-height: 100vh;
    }

    .block-container {
        max-width: 780px !important;
        padding: 2rem 2rem 4rem !important;
    }

    /* ── HERO BANNER ── */
    .hero-banner {
        background: linear-gradient(135deg, #0a3d62 0%, #1a6fa3 60%, #1db980 100%);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.8rem;
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
        font-size: 1.9rem;
        color: #ffffff;
        margin: 0 0 0.4rem 0;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.72);
        margin: 0;
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
    }

    /* ── PROGRESS STEPPER ── */
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
    .step-dot.done   { background: #1db980; color: #fff; }
    .step-dot.active { background: #1a6fa3; color: #fff; }
    .step-dot.pending{ background: #e8edf2; color: #94a3b8; }
    .step-line { flex: 1; height: 2px; background: #e8edf2; border-radius: 2px; }
    .step-line.done  { background: #1db980; }
    .step-label { font-size: 0.72rem; color: #64748b; font-weight: 500; white-space: nowrap; }
    .step-label.done { color: #1db980; font-weight: 600; }
    .step-label.active { color: #1a6fa3; font-weight: 600; }

    /* ── CARD ── */
    .card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.05);
        border: 1px solid #e2ecf5;
    }

    /* ── SNAPSHOT GRID ── */
    .snap-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 0.2rem;
    }
    .snap-item {
        background: #f4f8fd;
        border: 1px solid #dde8f4;
        border-radius: 12px;
        padding: 0.75rem 1rem;
    }
    .snap-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.3rem;
    }
    .snap-value {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
    }

    /* ── SECTION HEADER ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 1.1rem;
        padding-bottom: 0.75rem;
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
    .section-title-text { font-size: 0.97rem; font-weight: 700; color: #1e293b; margin: 0; }
    .section-desc-text  { font-size: 0.78rem; color: #94a3b8; margin: 0; }

    /* ── ANIMATED PULSE LOADER ── */
    .loader-outer {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1.5rem 0 1rem;
    }
    .pulse-ring-wrap {
        position: relative;
        width: 90px; height: 90px;
        margin-bottom: 1.2rem;
    }
    .pulse-ring {
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 3px solid transparent;
        border-top-color: #1a6fa3;
        border-right-color: #1db980;
        animation: spin 1.1s cubic-bezier(0.4,0,0.2,1) infinite;
    }
    .pulse-ring-2 {
        position: absolute;
        inset: 10px;
        border-radius: 50%;
        border: 2px solid transparent;
        border-bottom-color: #1a6fa3;
        border-left-color: #1db980;
        animation: spin 0.8s cubic-bezier(0.4,0,0.2,1) infinite reverse;
        opacity: 0.6;
    }
    .pulse-center {
        position: absolute;
        inset: 22px;
        border-radius: 50%;
        background: linear-gradient(135deg, #e8f1fb, #e4f7ef);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    @keyframes spin {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loader-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1.4rem;
        color: #1e293b;
        margin-bottom: 0.3rem;
        text-align: center;
    }
    .loader-sub {
        font-size: 0.85rem;
        color: #64748b;
        text-align: center;
        line-height: 1.6;
        max-width: 380px;
    }

    /* ── STEP PIPELINE ── */
    .pipeline {
        margin-top: 1.2rem;
        display: flex;
        flex-direction: column;
        gap: 0;
    }
    .pipeline-step {
        display: flex;
        align-items: flex-start;
        gap: 0.9rem;
        padding: 0.65rem 0;
        border-bottom: 1px solid #f0f4f8;
        transition: all 0.3s;
    }
    .pipeline-step:last-child { border-bottom: none; }
    .pipe-icon {
        width: 32px; height: 32px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
        margin-top: 0.1rem;
    }
    .pipe-icon.waiting  { background: #f1f5f9; }
    .pipe-icon.running  { background: #dbeafe; animation: pulse-bg 1s ease-in-out infinite alternate; }
    .pipe-icon.complete { background: #dcfce7; }
    .pipe-icon.error    { background: #fee2e2; }
    @keyframes pulse-bg {
        from { background: #dbeafe; }
        to   { background: #bfdbfe; }
    }
    .pipe-text { flex: 1; }
    .pipe-name {
        font-size: 0.88rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.1rem;
    }
    .pipe-name.muted { color: #94a3b8; font-weight: 500; }
    .pipe-desc {
        font-size: 0.76rem;
        color: #94a3b8;
    }
    .pipe-badge {
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        white-space: nowrap;
        align-self: center;
    }
    .pipe-badge.waiting  { background: #f1f5f9; color: #94a3b8; }
    .pipe-badge.running  { background: #dbeafe; color: #1d4ed8; }
    .pipe-badge.complete { background: #dcfce7; color: #166534; }
    .pipe-badge.error    { background: #fee2e2; color: #b91c1c; }

    /* ── PROGRESS BAR ── */
    div.stProgress > div > div > div > div {
        background: linear-gradient(90deg, #1a6fa3 0%, #1db980 100%) !important;
        border-radius: 99px !important;
    }
    div.stProgress > div > div > div {
        border-radius: 99px !important;
        height: 8px !important;
        background: #e8edf4 !important;
    }

    /* ── ERROR CARD ── */
    .error-card {
        background: #fff8f8;
        border: 1.5px solid #fca5a5;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }
    .error-title { font-weight: 700; color: #b91c1c; font-size: 0.95rem; margin-bottom: 0.4rem; }
    .error-msg   { font-size: 0.85rem; color: #64748b; line-height: 1.6; font-family: monospace; }

    /* ── RETRY / BACK BUTTONS ── */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0a3d62 0%, #1a6fa3 60%, #1db980 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.65rem 1.2rem !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 14px rgba(10,61,98,0.2) !important;
        transition: all 0.2s !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(10,61,98,0.28) !important;
    }

    /* ── FOOTER ── */
    .footer-note {
        text-align: center;
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #e8edf4;
    }
    .footer-note strong { color: #64748b; }

    .stAlert { border-radius: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# Helpers (ไม่แตะ logic)
# ==========================================
def call_predict_api(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise RuntimeError("Invalid API payload: payload must be a dictionary.")
    try:
        response = requests.post(PREDICT_ENDPOINT, json=payload, timeout=API_TIMEOUT_SECONDS)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Cannot connect to the FastAPI server. Please make sure the API is running at http://127.0.0.1:8000")
    except requests.exceptions.Timeout:
        raise RuntimeError("The prediction API timed out.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API request failed: {str(e)}")
    try:
        response_json = response.json()
    except ValueError:
        raise RuntimeError(f"API returned a non-JSON response (status {response.status_code}).")
    if response.status_code != 200:
        detail = response_json.get("detail", "Unknown API error")
        raise RuntimeError(f"API error ({response.status_code}): {detail}")
    if response_json.get("status") != "success":
        raise RuntimeError("Prediction API did not return success status.")
    if "data" not in response_json:
        raise RuntimeError("Prediction API response is missing 'data' field.")
    if not isinstance(response_json["data"], dict):
        raise RuntimeError("Prediction API response field 'data' must be a dictionary.")
    return response_json


def api_health_check() -> bool:
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code != 200:
            return False
        return response.json().get("status") == "ok"
    except (requests.exceptions.RequestException, ValueError):
        return False


def redirect_to_input_with_warning():
    st.warning("⚠️ No patient input found. Redirecting to input page...")
    time.sleep(1.2)
    st.switch_page("pages/1_Health_Data_Input.py")
    st.stop()


def save_processing_error(message: str):
    st.session_state["processing_error"] = message


def display_value(value, default="N/A"):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


# ==========================================
# Session check
# ==========================================
data = get_patient_data()
api_payload = st.session_state.get("api_payload")

if not data or not isinstance(api_payload, dict):
    redirect_to_input_with_warning()

# ==========================================
# HERO BANNER
# ==========================================
st.markdown("""
<div class="hero-banner">
    <div class="hero-eyebrow">🩺 DiaScreen AI · Step 2 of 3</div>
    <h1 class="hero-title">Analysing Your Health Data</h1>
    <p class="hero-sub">Running AI inference and generating a personalised clinical screening summary.</p>
    <div class="hero-badge">⚡ AI Inference Engine</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# PROGRESS STEPPER
# ==========================================
st.markdown("""
<div class="progress-wrap">
    <div class="step-dot done">✓</div>
    <span class="step-label done">Health Profile</span>
    <div class="step-line done"></div>
    <div class="step-dot active">2</div>
    <span class="step-label active">AI Analysis</span>
    <div class="step-line"></div>
    <div class="step-dot pending">3</div>
    <span class="step-label">Results & Advice</span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# PATIENT SNAPSHOT CARD
# ==========================================
age_val     = display_value(data.get("age"))
gender_val  = display_value(data.get("gender")).title()
glucose_val = display_value(data.get("blood_glucose_level"))
gtype_val   = display_value(data.get("glucose_test_type")).title()
act_val     = display_value(data.get("physical_activity_level")).title()
htn_val     = "Yes" if int(data.get("hypertension", 0)) == 1 else "No"
fhx_val     = "Yes" if int(data.get("family_history_diabetes", 0)) == 1 else "No"
bmi_val     = display_value(data.get("bmi"))

st.markdown(f"""
<div class="card">
    <div class="section-header">
        <div class="section-icon-wrap blue">📋</div>
        <div>
            <p class="section-title-text">Patient Snapshot</p>
            <p class="section-desc-text">Data submitted for analysis</p>
        </div>
    </div>
    <div class="snap-grid">
        <div class="snap-item">
            <div class="snap-label">Age</div>
            <div class="snap-value">{age_val} yrs</div>
        </div>
        <div class="snap-item">
            <div class="snap-label">Gender</div>
            <div class="snap-value">{gender_val}</div>
        </div>
        <div class="snap-item">
            <div class="snap-label">BMI</div>
            <div class="snap-value">{bmi_val}</div>
        </div>
        <div class="snap-item">
            <div class="snap-label">Glucose ({gtype_val})</div>
            <div class="snap-value">{glucose_val} mg/dL</div>
        </div>
        <div class="snap-item">
            <div class="snap-label">Hypertension</div>
            <div class="snap-value">{htn_val}</div>
        </div>
        <div class="snap-item">
            <div class="snap-label">Family History</div>
            <div class="snap-value">{fhx_val}</div>
        </div>
        <div class="snap-item">
            <div class="snap-label">Activity Level</div>
            <div class="snap-value">{act_val}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# ANIMATED LOADER + PIPELINE CARD
# ==========================================
st.markdown("""
<div class="card">
    <div class="section-header">
        <div class="section-icon-wrap green">🧠</div>
        <div>
            <p class="section-title-text">AI Screening Pipeline</p>
            <p class="section-desc-text">Live processing status</p>
        </div>
    </div>
    <div class="loader-outer">
        <div class="pulse-ring-wrap">
            <div class="pulse-ring"></div>
            <div class="pulse-ring-2"></div>
            <div class="pulse-center">🧬</div>
        </div>
        <div class="loader-title">Running Screening Model</div>
        <div class="loader-sub">Please wait while the AI analyses your health profile and generates clinical insights.</div>
    </div>
""", unsafe_allow_html=True)

progress_bar = st.progress(0)
status_placeholder = st.empty()

# Pipeline steps display
pipeline_placeholder = st.empty()

def render_pipeline(steps):
    """Render pipeline steps with status icons and badges."""
    icons    = {"waiting": "○", "running": "◉", "complete": "✓", "error": "✕"}
    rows = ""
    for s in steps:
        state = s["state"]
        rows += f"""
        <div class="pipeline-step">
            <div class="pipe-icon {state}">{icons[state]}</div>
            <div class="pipe-text">
                <div class="pipe-name {'muted' if state == 'waiting' else ''}">{s['name']}</div>
                <div class="pipe-desc">{s['desc']}</div>
            </div>
            <span class="pipe-badge {state}">{state.upper()}</span>
        </div>"""
    pipeline_placeholder.markdown(f'<div class="pipeline">{rows}</div>', unsafe_allow_html=True)

STEPS = [
    {"name": "API Health Check",        "desc": "Verify FastAPI server is reachable",          "state": "waiting"},
    {"name": "Payload Validation",      "desc": "Validate and serialise patient data",          "state": "waiting"},
    {"name": "Model Inference",         "desc": "Run diabetes classification model",            "state": "waiting"},
    {"name": "Result Interpretation",   "desc": "Parse prediction, probabilities & risk flags", "state": "waiting"},
    {"name": "Report Generation",       "desc": "Prepare clinical summary and recommendations", "state": "waiting"},
]

render_pipeline(STEPS)

st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PROCESSING FLOW (ไม่แตะ logic)
# ==========================================
def set_step(idx, state, progress, status_msg):
    for i, s in enumerate(STEPS):
        if i < idx:
            s["state"] = "complete"
        elif i == idx:
            s["state"] = state
        else:
            s["state"] = "waiting"
    render_pipeline(STEPS)
    progress_bar.progress(progress)
    status_placeholder.markdown(
        f"""<div style="background:#f0f7ff;border:1px solid #c6ddf5;border-radius:10px;
                        padding:0.7rem 1rem;font-size:0.85rem;color:#1a6fa3;
                        font-weight:500;margin-top:0.5rem;">
            ⟳ &nbsp;{status_msg}
        </div>""",
        unsafe_allow_html=True,
    )
    time.sleep(0.5)


try:
    # Step 0 — health check
    set_step(0, "running", 10, "Connecting to FastAPI screening service...")

    if not api_health_check():
        set_step(0, "error", 10, "Cannot reach FastAPI server.")
        error_msg = "Unable to connect to the FastAPI server. Please start the API: uvicorn api:app --reload"
        save_processing_error(error_msg)
        st.markdown(f"""
        <div class="error-card">
            <div class="error-title">🚨 Server Unreachable</div>
            <div class="error-msg">{error_msg}</div>
        </div>""", unsafe_allow_html=True)
        st.stop()

    set_step(0, "complete", 25, "API server is online and healthy.")

    # Step 1 — validation
    set_step(1, "running", 38, "Validating health data and preparing API request payload...")
    time.sleep(0.5)
    set_step(1, "complete", 50, "Payload validated successfully.")

    # Step 2 — inference
    set_step(2, "running", 62, "Running diabetes screening classification model...")

    api_response = call_predict_api(api_payload)

    set_step(2, "complete", 75, "Model inference completed.")

    # Step 3 — parse result
    set_step(3, "running", 85, "Parsing prediction scores and clinical risk flags...")
    prediction_result = api_response["data"]
    st.session_state["api_response"] = api_response
    st.session_state["prediction_result"] = prediction_result
    st.session_state["processing_error"] = None
    save_risk_result(prediction_result)
    save_api_response(api_response)
    time.sleep(0.4)
    set_step(3, "complete", 92, "Risk factors and clinical flags identified.")

    # Step 4 — report
    set_step(4, "running", 97, "Generating clinical summary and personalised recommendations...")
    time.sleep(0.5)
    set_step(4, "complete", 100, "Report ready. Redirecting to results…")

    # Final
    status_placeholder.markdown(
        """<div style="background:#e4f7ef;border:1px solid #a7e3cc;border-radius:10px;
                       padding:0.7rem 1rem;font-size:0.85rem;color:#0a5c40;font-weight:600;margin-top:0.5rem;">
            ✓ &nbsp;Analysis complete — loading your results now.
        </div>""",
        unsafe_allow_html=True,
    )
    time.sleep(0.8)
    st.switch_page("pages/3_AI_Risk_Analysis_Result.py")

except Exception as e:
    for s in STEPS:
        if s["state"] == "running":
            s["state"] = "error"
    render_pipeline(STEPS)
    progress_bar.progress(progress_bar)

    error_message = f"Prediction API Error: {str(e)}"
    save_processing_error(error_message)

    st.markdown(f"""
    <div class="error-card">
        <div class="error-title">🚨 Processing Failed</div>
        <div class="error-msg">{error_message}</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁  Retry Analysis", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("⬅️  Back to Input", use_container_width=True):
            st.switch_page("pages/1_Health_Data_Input.py")

    st.stop()

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer-note">
    DiaScreen AI · For screening purposes only · <strong>Not a medical diagnosis</strong><br>
    Always consult a licensed healthcare professional for clinical decisions.
</div>
""", unsafe_allow_html=True)