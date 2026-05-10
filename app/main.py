import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from db.connection import run_schema
from app.tabs import detect, history, about, news

st.set_page_config(
    page_title="NetConfirm — Fake News Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False

dark    = st.session_state["dark_mode"]
bg      = "#0f172a" if dark else "#ffffff"
card_bg = "#1e293b" if dark else "#f8fafc"
text    = "#f1f5f9" if dark else "#0f172a"
sub     = "#94a3b8" if dark else "#64748b"
border  = "#334155" if dark else "#e2e8f0"
accent  = "#1a1a2e"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*, html, body, [class*="css"] {{ font-family:'Inter',sans-serif !important; }}
div[data-testid="stAppViewContainer"] {{ background:{bg}; }}
div[data-testid="stHeader"] {{ background:transparent; }}
#MainMenu, footer, header {{ visibility:hidden; }}
.block-container {{ padding:1.5rem 2rem 3rem 2rem; max-width:1200px; margin:0 auto; }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap:0; border-bottom:2px solid {border}; background:transparent; padding:0;
}}
.stTabs [data-baseweb="tab"] {{
    font-size:14px; font-weight:500; color:{sub}; padding:10px 20px;
    border-radius:0; background:transparent; border:none;
}}
.stTabs [aria-selected="true"] {{
    color:{text}; font-weight:700;
    border-bottom:2px solid {accent}; margin-bottom:-2px; background:transparent;
}}

/* Inputs */
.stTextArea textarea, .stTextInput input {{
    border:1px solid {border} !important; border-radius:8px !important;
    font-size:14px !important; background:{card_bg} !important; color:{text} !important;
    padding:12px !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
    border-color:{accent} !important; box-shadow:0 0 0 3px {accent}18 !important;
}}

/* Buttons */
.stButton > button[kind="primary"] {{
    background:{accent}; color:white; border:none; border-radius:8px;
    font-size:14px; font-weight:600; padding:11px 24px; letter-spacing:0.2px;
    transition:all 0.15s; box-shadow:0 2px 8px {accent}40;
}}
.stButton > button[kind="primary"]:hover {{
    background:#2d2d4e; transform:translateY(-1px); box-shadow:0 4px 16px {accent}50;
}}
.stButton > button[kind="secondary"] {{
    background:{card_bg}; color:{text}; border:1px solid {border};
    border-radius:8px; font-size:13px; font-weight:500; padding:9px 18px;
}}
.stButton > button[kind="secondary"]:hover {{ background:{border}; }}

/* Metrics */
[data-testid="metric-container"] {{
    background:{card_bg}; border-radius:10px; padding:16px 20px;
    border:1px solid {border}; box-shadow:0 1px 4px rgba(0,0,0,0.04);
}}

/* Slider */
.stSlider [data-baseweb="slider"] {{ padding-top:6px; }}

/* Number input */
.stNumberInput input {{ background:{card_bg} !important; color:{text} !important; }}

/* Selectbox */
.stSelectbox > div > div {{ background:{card_bg}; color:{text}; border-color:{border}; }}

/* Scrollbar */
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:{border}; border-radius:3px; }}

/* Mobile */
@media (max-width: 768px) {{
    .block-container {{ padding:1rem; }}
    .stTabs [data-baseweb="tab"] {{ padding:8px 12px; font-size:13px; }}
}}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────
col_brand, col_right = st.columns([5, 1])
with col_brand:
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;padding:8px 0 4px 0;'>
        <div style='width:38px;height:38px;background:{accent};border-radius:10px;
            display:flex;align-items:center;justify-content:center;flex-shrink:0;'>
            <span style='font-size:18px;'>🔍</span>
        </div>
        <div>
            <div style='font-size:20px;font-weight:800;color:{text};letter-spacing:-0.5px;line-height:1;'>
                NetConfirm
            </div>
            <div style='font-size:12px;color:{sub};margin-top:2px;'>
                AI-powered fake news detection · DistilBERT + XGBoost
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("☀️" if dark else "🌙", key="theme_toggle", help="Toggle theme"):
        st.session_state["dark_mode"] = not dark
        st.rerun()

st.markdown(f"<div style='height:4px;background:{border};border-radius:2px;margin-bottom:20px;'></div>", unsafe_allow_html=True)

# ── Init DB ────────────────────────────────────────────────
@st.cache_resource
def init_db():
    try:
        run_schema()
    except Exception:
        pass

init_db()

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🔍  Detect", "📰  News", "📋  History", "ℹ️  About"])

with tab1:
    detect.render()
with tab2:
    news.render()
with tab3:
    history.render()
with tab4:
    about.render()
