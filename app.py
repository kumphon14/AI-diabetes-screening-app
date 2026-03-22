import streamlit as st

# 1. ตั้งค่า Page Configuration เป็นอันดับแรกเสมอ
st.set_page_config(
    page_title="DiaScreen AI - Diabetes Risk Assessment",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed" # ปิด sidebar ในหน้าแรกเพื่อให้เหมือน Web App
)
def load_local_css(file_name="assets/style.css"):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"⚠️ ไม่พบไฟล์ CSS ที่ path: {file_name}")

# 2. ฟังก์ชันสำหรับ Inject Custom CSS ให้หน้าตาเหมือน Tailwind Prototype
def local_css():
    st.markdown("""
        <style>
        /* Import Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Prompt:wght@300;400;500;600;700&display=swap');
        
        /* Global Font and Background */
        html, body, [class*="css"] {
            font-family: 'Inter', 'Prompt', sans-serif;
        }
        
        /* เปลี่ยนสีพื้นหลังหลักของ Streamlit */
        .stApp {
            background-color: #f3f4f6;
        }
        
        /* ซ่อน Header และ Footer ของ Streamlit เพื่อความคลีน */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* ตกแต่งปุ่ม Streamlit ให้เหมือน Tailwind Button */
        div.stButton > button:first-child {
            background-color: #2563eb;
            color: white;
            border-radius: 0.75rem;
            padding: 0.75rem 2rem;
            font-size: 1.125rem;
            font-weight: 500;
            border: none;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            transition: all 0.2s ease-in-out;
            width: 100%;
        }
        div.stButton > button:first-child:hover {
            background-color: #1d4ed8;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }
        
        /* Navbar Mockup CSS */
        .custom-navbar {
            background-color: white;
            padding: 1rem 2rem;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999;
        }
        .navbar-brand {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0f172a;
            display: flex;
            align-items: center;
        }
        .navbar-brand span {
            color: #2563eb;
            font-weight: 400;
            margin-left: 4px;
        }
        
        /* Hero Section CSS */
        .hero-badge {
            display: inline-flex;
            align-items: center;
            background-color: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #dbeafe;
            border-radius: 9999px;
            padding: 0.375rem 1rem;
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }
        .hero-badge-dot {
            height: 0.5rem;
            width: 0.5rem;
            background-color: #3b82f6;
            border-radius: 50%;
            margin-right: 0.5rem;
            display: inline-block;
        }
        .hero-title {
            font-size: 3.75rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
            margin-bottom: 1rem;
        }
        .hero-title-blue {
            color: #2563eb;
        }
        .hero-subtitle {
            font-size: 1.125rem;
            color: #64748b;
            max-width: 42rem;
            margin: 0 auto;
            line-height: 1.5;
        }
        </style>
    """, unsafe_allow_html=True)

# 3. จัดการ Session State
def init_session_state():
    """เตรียมตัวแปรสำหรับการใช้งานข้ามหน้าเพจ"""
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {}
    if 'risk_result' not in st.session_state:
        st.session_state.risk_result = None

# ==========================================
# Main App Execution
# ==========================================
def main():
    local_css()
    init_session_state()

    # สร้าง Navbar จำลองด้านบน (ใช้ HTML)
    st.markdown("""
        <div class="custom-navbar">
            <div class="navbar-brand">
                🩺 DiaScreen <span>AI</span>
            </div>
            <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">
                Clinical Decision Support System
            </div>
        </div>
        <div style="margin-top: 5rem;"></div> """, unsafe_allow_html=True)

    # เว้นช่องว่างตรงกลางหน้าจอ
    st.write("<br><br>", unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
        <div style="text-align: center;">
            <div class="hero-badge">
                <span class="hero-badge-dot"></span> Prototype v2.0 Live
            </div>
            <h1 class="hero-title">
                AI-Based <span class="hero-title-blue">Diabetes Risk</span><br>Prediction System
            </h1>
            <p class="hero-subtitle">
                Intelligent screening support tool combining Machine Learning probabilities with rule-based clinical flags to assist in early diabetes detection.
            </p>
        </div>
        <br><br>
    """, unsafe_allow_html=True)

    # ปุ่มตรงกลางสำหรับไปหน้าถัดไป
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("New Patient Assessment ➔", use_container_width=True):
            # ฟังก์ชันเปลี่ยนหน้าต่างของ Streamlit (ต้องการไฟล์ 1_Health_Data_Input.py)
            try:
                st.switch_page("pages/1_Health_Data_Input.py")
            except Exception as e:
                st.error("⚠️ ไม่พบไฟล์ `pages/1_Health_Data_Input.py` กรุณาสร้างโฟลเดอร์ pages และไฟล์ดังกล่าวก่อนครับ")

    # Footer
    st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: white; padding: 1.5rem; text-align: center; border-top: 1px solid #e5e7eb; color: #94a3b8; font-size: 0.875rem;">
            &copy; 2026 AI-Based Diabetes Risk Prediction System Prototype.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()