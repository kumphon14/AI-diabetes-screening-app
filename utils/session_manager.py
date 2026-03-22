import streamlit as st

# ==========================================
# Initialize session state (safe defaults)
# ==========================================
def init_session_state():
    """
    Ensure all required session keys exist.
    Call this at the top of every page.
    """
    default_keys = {
        "patient_data": None,
        "api_payload": None,
        "screening_result": None,   # new primary key
        "risk_result": None,        # backward compatibility
        "api_response": None,
        "prediction_result": None,
        "processing_error": None,
    }

    for key, default_value in default_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


# ==========================================
# Patient Data (UI input)
# ==========================================
def save_patient_data(data: dict):
    """
    Save raw patient data from UI.
    """
    if not isinstance(data, dict):
        raise ValueError("patient_data must be a dictionary")

    st.session_state["patient_data"] = data


def get_patient_data():
    """
    Retrieve patient data.
    """
    return st.session_state.get("patient_data", None)


# ==========================================
# API Payload (what we send to FastAPI)
# ==========================================
def save_api_payload(payload: dict):
    """
    Save payload prepared for API call.
    """
    if not isinstance(payload, dict):
        raise ValueError("api_payload must be a dictionary")

    st.session_state["api_payload"] = payload


def get_api_payload():
    """
    Retrieve API payload.
    """
    return st.session_state.get("api_payload", None)


# ==========================================
# Screening Result (new primary result)
# ==========================================
def save_screening_result(result: dict):
    """
    Save processed screening result returned from FastAPI.
    This should be response['data'] from /predict.
    """
    if not isinstance(result, dict):
        raise ValueError("screening_result must be a dictionary")

    st.session_state["screening_result"] = result

    # backward compatibility for pages/functions
    # that still use the old risk_result key
    st.session_state["risk_result"] = result

    # optional mirror for debug/inspection
    st.session_state["prediction_result"] = result


def get_screening_result():
    """
    Retrieve screening result for UI display.
    Prefer this function in new code.
    """
    result = st.session_state.get("screening_result", None)

    # fallback to legacy key if needed
    if result is None:
        result = st.session_state.get("risk_result", None)

    return result


# ==========================================
# Backward Compatibility (legacy naming)
# ==========================================
def save_risk_result(result: dict):
    """
    Legacy alias for save_screening_result().
    Kept temporarily for backward compatibility.
    """
    save_screening_result(result)


def get_risk_result():
    """
    Legacy alias for get_screening_result().
    Kept temporarily for backward compatibility.
    """
    return get_screening_result()


# ==========================================
# Optional Debug Storage
# ==========================================
def save_api_response(response: dict):
    """
    Save full API response (including metadata).
    """
    if not isinstance(response, dict):
        raise ValueError("api_response must be a dictionary")

    st.session_state["api_response"] = response


def get_api_response():
    return st.session_state.get("api_response", None)


def save_prediction_result(result: dict):
    """
    Save prediction result separately for debug/inspection if needed.
    """
    if not isinstance(result, dict):
        raise ValueError("prediction_result must be a dictionary")

    st.session_state["prediction_result"] = result


def get_prediction_result():
    return st.session_state.get("prediction_result", None)


# ==========================================
# Processing Error
# ==========================================
def save_processing_error(message: str | None):
    """
    Save processing error message for UI handling.
    """
    if message is not None and not isinstance(message, str):
        raise ValueError("processing_error must be a string or None")

    st.session_state["processing_error"] = message


def get_processing_error():
    return st.session_state.get("processing_error", None)


def clear_processing_error():
    st.session_state["processing_error"] = None


# ==========================================
# Clear Session (reset app)
# ==========================================
def clear_session():
    """
    Clear only relevant app session data (safe reset).
    Do NOT nuke entire session_state to avoid Streamlit issues.
    """
    keys_to_clear = [
        "patient_data",
        "api_payload",
        "screening_result",
        "risk_result",
        "api_response",
        "prediction_result",
        "processing_error",
    ]

    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    init_session_state()