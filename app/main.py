import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from db.connection import run_schema
from app.tabs import detect, history, about, news

st.set_page_config(
    page_title="NetConfirm",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme init ─────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

dark = st.session_state["dark_mode"]
bg       = "#0f172a" if dark else "#ffffff"
card_bg  = "#1e293b" if dark else "#f8fafc"
text     = "#f1f5f9" if dark else "#18181b"
sub      = "#94a3b8" if dark else "#71717a"
border   = "#334155" if dark else "#e4e4e7"
tab_sel  = "#f1f5f9" if dark else "#18181b"
accent   = "#1a1a2e"

# ── Global CSS ─────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background: {bg}; color: {text}; }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1100px; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {border}; background: transparent; }}
    .stTabs [data-baseweb="tab"] {{ font-size: 14px; font-weight: 500; color: {sub}; padding: 8px 18px; border-radius: 6px 6px 0 0; background: transparent; }}
    .stTabs [aria-selected="true"] {{ color: {tab_sel}; border-bottom: 2px solid {accent}; background: transparent; }}
    .stTextArea textarea, .stTextInput input {{
        border: 1px solid {border}; border-radius: 8px; font-size: 14px;
        font-family: 'Inter', sans-serif; background: {card_bg}; color: {text};
    }}
    .stTextArea textarea:focus, .stTextInput input:focus {{
        border-color: {accent}; box-shadow: 0 0 0 2px {accent}22;
    }}
    .stButton > button[kind="primary"] {{
        background: {accent}; color: white; border: none; border-radius: 8px;
        font-size: 14px; font-weight: 600; padding: 10px 24px; transition: background 0.2s;
    }}
    .stButton > button[kind="primary"]:hover {{ background: #2d2d4e; }}
    .stButton > button[kind="secondary"] {{
        background: {card_bg}; color: {text}; border: 1px solid {border};
        border-radius: 8px; font-size: 13px; font-weight: 500;
    }}
    [data-testid="metric-container"] {{
        background: {card_bg}; border-radius: 8px; padding: 12px 16px; border: 1px solid {border};
    }}
    hr {{ border: none; border-top: 1px solid {border}; margin: 20px 0; }}
    .stSlider [data-baseweb="slider"] {{ padding-top: 4px; }}
    .stSelectbox > div, .stNumberInput > div {{ background: {card_bg}; }}
    div[data-testid="stAppViewContainer"] {{ background: {bg}; }}
    section[data-testid="stSidebar"] {{ background: {card_bg}; }}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────
col_logo, col_toggle = st.columns([6, 1])
with col_logo:
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:4px;padding-top:4px;'>
        <span style='font-size:24px;'>🔍</span>
        <span style='font-size:22px;font-weight:800;color:{text};letter-spacing:-0.5px;'>NetConfirm</span>
    </div>
    <p style='font-size:13px;color:{sub};margin:0 0 16px 0;'>
        Hybrid fake news detection · DistilBERT + XGBoost · WELFake trained
    </p>
    """, unsafe_allow_html=True)

with col_toggle:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    toggle_label = "☀️ Light" if dark else "🌙 Dark"
    if st.button(toggle_label, key="theme_toggle"):
        st.session_state["dark_mode"] = not dark
        st.rerun()

# ── Init DB ────────────────────────────────────────────────
@st.cache_resource
def init_db():
    try:
        run_schema()
    except Exception as e:
        st.warning(f"Database initialisation warning: {e}")

init_db()

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Detect", "📰 News", "📋 History", "ℹ️ About"])

with tab1:
    detect.render()

with tab2:
    news.render()

with tab3:
    history.render()

with tab4:
    about.render()
