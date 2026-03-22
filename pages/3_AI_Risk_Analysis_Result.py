import streamlit as st
import sys
import os
import time
import html

# ==========================================
# Import session utilities
# ==========================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.session_manager import get_screening_result, clear_session, init_session_state

# ==========================================
# Page config
# ==========================================
st.set_page_config(
    page_title="Diabetes Screening Result | DiaScreen AI",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed",
)
init_session_state()

# ==========================================
# CSS — matches Page 1 & 2 design system
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
        background-color: #f0f4f8 !important;
    }

    header {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── PAGE BG ── */
    .stApp {
        background: linear-gradient(160deg, #eaf3ff 0%, #f0f7f4 50%, #f0f4f8 100%) !important;
        min-height: 100vh;
    }
    .block-container {
        max-width: 860px !important;
        padding: 2rem 2rem 4rem !important;
    }

    /* ── HERO BANNER ── */
    .hero-banner {
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(10, 61, 98, 0.18);
    }
    .hero-banner.positive {
        background: linear-gradient(135deg, #7c1d1d 0%, #b91c1c 55%, #dc6803 100%);
    }
    .hero-banner.negative {
        background: linear-gradient(135deg, #0a3d62 0%, #1a6fa3 60%, #1db980 100%);
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
        background: rgba(255,255,255,0.06);
        border-radius: 50%;
    }
    .hero-eyebrow {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.7);
        margin-bottom: 0.4rem;
    }
    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1.85rem;
        color: #ffffff;
        margin: 0 0 0.35rem 0;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 0.88rem;
        color: rgba(255,255,255,0.75);
        margin: 0 0 1rem 0;
        max-width: 520px;
        line-height: 1.6;
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
    .result-verdict {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1.2rem;
        border-radius: 40px;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        border: 1.5px solid rgba(255,255,255,0.3);
        background: rgba(255,255,255,0.15);
        color: #fff;
        margin-right: 0.5rem;
    }

    /* ── STEPPER ── */
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
    .step-dot { width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.72rem; font-weight:700; flex-shrink:0; }
    .step-dot.done   { background:#1db980; color:#fff; }
    .step-dot.active { background:#1a6fa3; color:#fff; }
    .step-dot.pending{ background:#e8edf2; color:#94a3b8; }
    .step-line { flex:1; height:2px; background:#e8edf2; border-radius:2px; }
    .step-line.done  { background:#1db980; }
    .step-label { font-size:0.72rem; color:#64748b; font-weight:500; white-space:nowrap; }
    .step-label.done   { color:#1db980; font-weight:600; }
    .step-label.active { color:#1a6fa3; font-weight:600; }

    /* ── STAT CARDS ── */
    .stat-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 1.2rem;
    }
    .stat-card {
        background: #ffffff;
        border: 1px solid #e2ecf5;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        text-align: center;
    }
    .stat-card.accent-pos { border-top: 3px solid #dc2626; }
    .stat-card.accent-neg { border-top: 3px solid #1db980; }
    .stat-card.accent-neu { border-top: 3px solid #1a6fa3; }
    .stat-label {
        font-size: 0.68rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        margin-bottom: 0.4rem;
    }
    .stat-value {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.3;
    }
    .stat-value.pos { color: #b91c1c; }
    .stat-value.neg { color: #0a5c40; }

    /* ── CARDS ── */
    .card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 16px rgba(0,0,0,0.05);
        border: 1px solid #e2ecf5;
    }

    /* ── SECTION HEADER ── */
    .sec-header {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1.5px solid #eef3f9;
    }
    .sec-icon {
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }
    .sec-icon.red    { background: #fef2f2; }
    .sec-icon.blue   { background: #e8f1fb; }
    .sec-icon.green  { background: #e4f7ef; }
    .sec-icon.amber  { background: #fef3e2; }
    .sec-icon.purple { background: #f3f0ff; }
    .sec-title { font-size: 0.97rem; font-weight: 700; color: #1e293b; margin: 0; }
    .sec-desc  { font-size: 0.76rem; color: #94a3b8; margin: 0; }

    /* ── VERDICT BLOCK ── */
    .verdict-block {
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.9rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }
    .verdict-block.pos {
        background: linear-gradient(135deg, #fff7f7, #fff1f1);
        border: 1.5px solid #fca5a5;
    }
    .verdict-block.neg {
        background: linear-gradient(135deg, #f0fdf9, #e9fdf5);
        border: 1.5px solid #6ee7b7;
    }
    .verdict-icon {
        font-size: 2rem;
        line-height: 1;
        flex-shrink: 0;
    }
    .verdict-heading {
        font-family: 'DM Serif Display', serif;
        font-size: 1.15rem;
        margin: 0 0 0.3rem 0;
    }
    .verdict-heading.pos { color: #991b1b; }
    .verdict-heading.neg { color: #065f46; }
    .verdict-body {
        font-size: 0.88rem;
        color: #475569;
        line-height: 1.65;
        margin: 0;
    }

    /* ── INTERPRETATION ── */
    .interp-box {
        border-radius: 12px;
        padding: 1rem 1.15rem;
        font-size: 0.88rem;
        line-height: 1.75;
        color: #334155;
        border-left: 4px solid;
    }
    .interp-box.blue  { background: #f0f7ff; border-color: #1a6fa3; }
    .interp-box.amber { background: #fffbeb; border-color: #f59e0b; }

    /* ── LIST ITEMS ── */
    .item-list { display:flex; flex-direction:column; gap:8px; }
    .item-row {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        background: #f8fafd;
        border: 1px solid #e8eef7;
        border-radius: 12px;
        padding: 0.75rem 0.9rem;
        transition: background 0.15s;
    }
    .item-row:hover { background: #f0f5fc; }
    .item-icon {
        width: 28px; height: 28px; min-width: 28px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.82rem;
        font-weight: 700;
        margin-top: 1px;
        flex-shrink: 0;
    }
    .icon-flag   { background: #fff1f2; color: #be123c; }
    .icon-factor { background: #eff6ff; color: #1d4ed8; }
    .icon-rec    { background: #f0fdf4; color: #15803d; }
    .item-text {
        font-size: 0.875rem;
        color: #334155;
        line-height: 1.65;
    }
    .empty-state {
        border: 1.5px dashed #cbd5e1;
        background: #f8fafc;
        color: #94a3b8;
        border-radius: 12px;
        padding: 0.9rem 1rem;
        font-size: 0.85rem;
        font-style: italic;
        text-align: center;
    }

    /* ── DIVIDER ── */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2ecf5, transparent);
        margin: 0.5rem 0 1rem;
    }

    /* ── DISCLAIMER ── */
    .disclaimer {
        background: #fffdf5;
        border: 1px solid #fde68a;
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        color: #78350f;
        font-size: 0.8rem;
        line-height: 1.7;
        margin-top: 1.4rem;
    }
    .disclaimer strong { color: #92400e; }

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

    /* ── BUTTON ── */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0a3d62 0%, #1a6fa3 60%, #1db980 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.4rem !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        box-shadow: 0 4px 14px rgba(10,61,98,0.2) !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(10,61,98,0.28) !important;
    }

    .stAlert { border-radius: 12px !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# Helpers (ไม่แตะ logic)
# ==========================================
def safe_int(value, default=None):
    try:
        return int(value)
    except Exception:
        return default

def safe_list(value):
    return value if isinstance(value, list) else []

def safe_text(value, default="N/A"):
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default

def escape_text(value):
    return html.escape(str(value))

def render_info_list(items, icon_class, icon_symbol, empty_text):
    if not items:
        st.markdown(f"<div class='empty-state'>{escape_text(empty_text)}</div>", unsafe_allow_html=True)
        return
    cleaned = [str(i).strip() for i in items if str(i).strip()]
    if not cleaned:
        st.markdown(f"<div class='empty-state'>{escape_text(empty_text)}</div>", unsafe_allow_html=True)
        return
    rows = "".join(
        f'<div class="item-row"><div class="item-icon {icon_class}">{escape_text(icon_symbol)}</div>'
        f'<div class="item-text">{escape_text(item)}</div></div>'
        for item in cleaned
    )
    st.markdown(f'<div class="item-list">{rows}</div>', unsafe_allow_html=True)

# ==========================================
# Session check (ไม่แตะ logic)
# ==========================================
res = get_screening_result()
if not res:
    st.warning("⚠️ No screening results found. Redirecting to input page.")
    time.sleep(1.2)
    st.switch_page("pages/1_Health_Data_Input.py")
    st.stop()

# ==========================================
# Extract data (ไม่แตะ logic)
# ==========================================
predicted_class      = safe_int(res.get("predicted_class"), None)
prediction_code      = safe_text(res.get("prediction_code"), "unknown").lower()
prediction_label     = safe_text(res.get("prediction_label"), "N/A")
screening_result     = safe_text(res.get("screening_result"), "N/A")
short_interpretation = safe_text(res.get("short_interpretation"), "No interpretation available.")
clinical_flags       = safe_list(res.get("clinical_flags", []))
key_risk_factors     = safe_list(res.get("key_risk_factors", []))
recommendations      = safe_list(res.get("recommendations", []))

is_positive = prediction_code == "positive" or predicted_class == 1

banner_cls    = "positive" if is_positive else "negative"
verdict_cls   = "pos"      if is_positive else "neg"
accent_cls    = "accent-pos" if is_positive else "accent-neg"
stat_val_cls  = "pos"      if is_positive else "neg"
interp_cls    = "amber"    if clinical_flags else "blue"

verdict_icon    = "⚠️" if is_positive else "✅"
verdict_heading = "Elevated Diabetes Risk Detected" if is_positive else "No Strong Diabetes Risk Detected"
verdict_body    = (
    "The AI screening model indicates a higher likelihood of diabetes based on your submitted health data. "
    "Clinical follow-up and confirmatory testing are strongly recommended."
    if is_positive else
    "The AI screening model does not strongly suggest diabetes at this time. "
    "Maintaining a healthy lifestyle and routine check-ups remain important."
)
hero_eyebrow = "🩺 DiaScreen AI · Step 3 of 3 · Screening Complete"

# ==========================================
# HERO BANNER
# ==========================================
st.markdown(f"""
<div class="hero-banner {banner_cls}">
    <div class="hero-badge">📋 AI Result Report</div>
    <div class="hero-eyebrow">{hero_eyebrow}</div>
    <h1 class="hero-title">Diabetes Screening Result</h1>
    <p class="hero-sub">
        AI-generated screening summary with clinical flags, key risk factors,
        and personalised follow-up recommendations.
    </p>
    <div>
        <span class="result-verdict">{verdict_icon} {escape_text(screening_result)}</span>
        <span class="result-verdict">🤖 {escape_text(prediction_label)}</span>
    </div>
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
    <div class="step-dot done">✓</div>
    <span class="step-label done">AI Analysis</span>
    <div class="step-line done"></div>
    <div class="step-dot active">3</div>
    <span class="step-label active">Results & Advice</span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# STAT SUMMARY ROW
# ==========================================
st.markdown(f"""
<div class="stat-row">
    <div class="stat-card {accent_cls}">
        <div class="stat-label">Screening Result</div>
        <div class="stat-value {stat_val_cls}">{escape_text(screening_result)}</div>
    </div>
    <div class="stat-card accent-neu">
        <div class="stat-label">AI Prediction</div>
        <div class="stat-value">{escape_text(prediction_label)}</div>
    </div>
    <div class="stat-card {'accent-pos' if clinical_flags else 'accent-neg'}">
        <div class="stat-label">Clinical Flags</div>
        <div class="stat-value {('pos' if clinical_flags else 'neg')}">
            {len(clinical_flags)} {'Flagged' if clinical_flags else 'None'}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# ACTION BUTTON
# ==========================================
col_l, col_btn, col_r = st.columns([1, 1.6, 1])
with col_btn:
    if st.button("🔄  Start New Assessment", use_container_width=True):
        clear_session()
        st.switch_page("pages/1_Health_Data_Input.py")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# MAIN RESULT CARD
# ==========================================
st.markdown(f"""
<div class="card">
    <div class="sec-header">
        <div class="sec-icon {'red' if is_positive else 'green'}">{'⚠️' if is_positive else '✅'}</div>
        <div>
            <p class="sec-title">Main Screening Verdict</p>
            <p class="sec-desc">AI classification outcome</p>
        </div>
    </div>
    <div class="verdict-block {verdict_cls}">
        <div class="verdict-icon">{verdict_icon}</div>
        <div>
            <p class="verdict-heading {verdict_cls}">{verdict_heading}</p>
            <p class="verdict-body">{escape_text(verdict_body)}</p>
        </div>
    </div>
    <div class="divider"></div>
    <div class="interp-box {interp_cls}">
        <strong>AI Interpretation:</strong> {escape_text(short_interpretation)}
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# CLINICAL FLAGS CARD
# ==========================================
st.markdown(f"""
<div class="card">
    <div class="sec-header">
        <div class="sec-icon red">🚩</div>
        <div>
            <p class="sec-title">Clinical Flags</p>
            <p class="sec-desc">Elevated or abnormal values from submitted data</p>
        </div>
    </div>
""", unsafe_allow_html=True)
render_info_list(
    clinical_flags,
    icon_class="icon-flag",
    icon_symbol="!",
    empty_text="No major clinical warning flags were identified for this screening result.",
)
st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# KEY RISK FACTORS + RECOMMENDATIONS (2-col)
# ==========================================
col_a, col_b = st.columns(2, gap="medium")

with col_a:
    st.markdown(f"""
    <div class="card" style="height:100%">
        <div class="sec-header">
            <div class="sec-icon blue">🔍</div>
            <div>
                <p class="sec-title">Key Risk Factors</p>
                <p class="sec-desc">Contributing variables identified</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    render_info_list(
        key_risk_factors,
        icon_class="icon-factor",
        icon_symbol="•",
        empty_text="No major risk factors were highlighted from the available inputs.",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
    <div class="card" style="height:100%">
        <div class="sec-header">
            <div class="sec-icon green">💡</div>
            <div>
                <p class="sec-title">Recommendations</p>
                <p class="sec-desc">Suggested next steps</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    render_info_list(
        recommendations,
        icon_class="icon-rec",
        icon_symbol="✓",
        empty_text="Maintain healthy lifestyle habits and continue routine screening as appropriate.",
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# DISCLAIMER
# ==========================================
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Medical Disclaimer:</strong> This result is generated by an AI-based screening support system and
    is <strong>not a medical diagnosis</strong>. The output should be interpreted alongside symptoms,
    clinical history, physical examination, and professional medical judgment.
    Please consult a qualified healthcare professional for diagnosis, confirmatory testing,
    or any treatment decisions.
</div>
""", unsafe_allow_html=True)

# ==========================================
# FOOTER
# ==========================================
st.markdown("""
<div class="footer-note">
    DiaScreen AI · For screening purposes only · <strong>Not a medical diagnosis</strong><br>
    Always consult a licensed healthcare professional for clinical decisions.
</div>
""", unsafe_allow_html=True)