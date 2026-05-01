import streamlit as st
from db.connection import run_schema
from app.tabs import detect, history, about

st.set_page_config(
    page_title="NetConfirm",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Clean container */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 860px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #e4e4e7;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 14px;
        font-weight: 500;
        color: #71717a;
        padding: 8px 16px;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #18181b;
        border-bottom: 2px solid #1a1a2e;
        background: transparent;
    }

    /* Inputs */
    .stTextArea textarea, .stTextInput input {
        border: 1px solid #e4e4e7;
        border-radius: 8px;
        font-size: 14px;
        font-family: 'Inter', sans-serif;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #1a1a2e;
        box-shadow: 0 0 0 2px #1a1a2e22;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        background: #1a1a2e;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        padding: 10px 24px;
        transition: background 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        background: #2d2d4e;
    }

    /* Metrics */
    [data-testid="metric-container"] {
        background: #f4f4f5;
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid #e4e4e7;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #e4e4e7;
        margin: 20px 0;
    }

    /* Slider */
    .stSlider [data-baseweb="slider"] {
        padding-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom: 24px'>
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:4px'>
        <span style='font-size:24px'>🔍</span>
        <span style='font-size:22px;font-weight:700;color:#18181b;letter-spacing:-0.5px'>NetConfirm</span>
    </div>
    <p style='font-size:13px;color:#71717a;margin:0'>
        Hybrid fake news detection · DistilBERT + XGBoost · WELFake trained
    </p>
</div>
""", unsafe_allow_html=True)

# ── Init DB ────────────────────────────────────────────────
@st.cache_resource
def init_db():
    try:
        run_schema()
    except Exception as e:
        st.warning(f"Database initialisation warning: {e}")

init_db()

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Detect", "History", "About"])

with tab1:
    detect.render()

with tab2:
    history.render()

with tab3:
    about.render()
