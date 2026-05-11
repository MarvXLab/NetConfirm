import sys
import os
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a dummy secrets file so Streamlit stops warning about it
for _p in ["/opt/render/.streamlit", "/opt/render/project/src/.streamlit"]:
    try:
        os.makedirs(_p, exist_ok=True)
        _sf = os.path.join(_p, "secrets.toml")
        if not os.path.exists(_sf):
            open(_sf, "w").close()
    except Exception:
        pass

import streamlit as st
from db.connection import run_schema
from app.tabs import detect, history, about, news

st.set_page_config(
    page_title="NetConfirm — Fake News Detector",
    page_icon="https://cdn-icons-png.flaticon.com/128/681/681508.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "detect"

dark   = st.session_state["dark_mode"]
page   = st.session_state["page"]
bg     = "#0f172a" if dark else "#ffffff"
card   = "#1e293b" if dark else "#f8fafc"
text   = "#f1f5f9" if dark else "#0f172a"
sub    = "#94a3b8" if dark else "#64748b"
border = "#334155" if dark else "#e2e8f0"
accent = "#1a1a2e"
F      = "invert(14%) sepia(20%) saturate(800%) hue-rotate(190deg) brightness(80%) contrast(95%)"
FW     = "brightness(0) invert(1)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*, html, body, [class*="css"] {{ font-family:'Inter',sans-serif !important; }}
div[data-testid="stAppViewContainer"] {{ background:{bg}; }}
div[data-testid="stHeader"] {{ display:none; }}
#MainMenu, footer, header {{ visibility:hidden; }}
.block-container {{ padding:0 !important; max-width:100% !important; }}

.stTextArea textarea, .stTextInput input {{
    border:1px solid {border} !important; border-radius:8px !important;
    font-size:14px !important; background:{card} !important; color:{text} !important; padding:12px !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
    border-color:{accent} !important; box-shadow:0 0 0 3px {accent}18 !important;
}}
.stButton > button[kind="primary"] {{
    background:{accent}; color:white; border:none; border-radius:8px;
    font-size:14px; font-weight:600; padding:11px 24px;
    transition:all 0.15s; box-shadow:0 2px 8px {accent}40;
}}
.stButton > button[kind="primary"]:hover {{ background:#2d2d4e; transform:translateY(-1px); }}
.stButton > button[kind="secondary"] {{
    background:{card}; color:{text}; border:1px solid {border};
    border-radius:8px; font-size:13px; font-weight:500; padding:9px 18px;
}}
[data-testid="metric-container"] {{
    background:{card}; border-radius:10px; padding:16px 20px; border:1px solid {border};
}}
.stSlider [data-baseweb="slider"] {{ padding-top:6px; }}
.stNumberInput input {{ background:{card} !important; color:{text} !important; }}
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-thumb {{ background:{border}; border-radius:3px; }}

/* Navbar */
.nc-nav {{
    background:{card}; border-bottom:1px solid {border};
    padding:0 16px; display:flex; align-items:center;
    justify-content:space-between; height:60px; position:sticky; top:0; z-index:100;
    box-shadow:0 1px 8px rgba(0,0,0,{'0.3' if dark else '0.06'});
}}
.nc-brand {{ display:flex; align-items:center; gap:10px; }}
.nc-brand-icon {{
    width:34px; height:34px; background:{accent}; border-radius:9px;
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
}}
.nc-brand-name {{ font-size:17px; font-weight:800; color:{text}; letter-spacing:-0.5px; }}
.nc-brand-sub {{ font-size:10px; color:{sub}; line-height:1; }}

/* Tab nav bar */
.nc-tabs {{
    background:{card}; border-bottom:1px solid {border};
    display:flex; align-items:center; gap:2px; padding:0 16px;
    overflow-x:auto; scrollbar-width:none;
}}
.nc-tabs::-webkit-scrollbar {{ display:none; }}
.nc-tab {{
    display:flex; align-items:center; gap:6px; padding:12px 16px;
    font-size:13px; font-weight:500; color:{sub}; cursor:pointer;
    border:none; background:transparent; white-space:nowrap;
    border-bottom:2px solid transparent; transition:all 0.15s;
    text-decoration:none;
}}
.nc-tab:hover {{ color:{text}; }}
.nc-tab.active {{ color:{text}; border-bottom:2px solid {accent}; font-weight:600; }}
.nc-tab img {{ width:15px; height:15px; object-fit:contain; }}
.nc-tab.active img {{ filter:{FW}; opacity:0.8; }}
.nc-tab:not(.active) img {{ filter:{F}; }}

.nc-content {{ padding:24px; max-width:1200px; margin:0 auto; }}
@media (max-width:640px) {{ .nc-content {{ padding:12px; }} .nc-brand-sub {{ display:none; }} }}
</style>
""", unsafe_allow_html=True)

# ── Navbar brand + theme toggle ─────────────────────────────
nav_items = [
    ("detect",  "https://cdn-icons-png.flaticon.com/128/681/681508.png",    "Detect"),
    ("news",    "https://cdn-icons-png.flaticon.com/128/11437/11437791.png", "News"),
    ("history", "https://cdn-icons-png.flaticon.com/128/8375/8375772.png",   "History"),
    ("about",   "https://cdn-icons-png.flaticon.com/128/17450/17450816.png", "About"),
]

tabs_html = ""
for p, icon, label in nav_items:
    active_cls = "active" if page == p else ""
    tabs_html += f"<a class='nc-tab {active_cls}' href='?page={p}'><img src='{icon}'>{label}</a>"

theme_emoji = "☀️" if dark else "🌙"

st.markdown(f"""
<nav class='nc-nav'>
    <div class='nc-brand'>
        <div class='nc-brand-icon'>
            <img src='https://cdn-icons-png.flaticon.com/128/681/681508.png'
                style='width:20px;height:20px;object-fit:contain;filter:brightness(0) invert(1);'>
        </div>
        <div>
            <div class='nc-brand-name'>NetConfirm</div>
            <div class='nc-brand-sub'>AI Fake News Detector</div>
        </div>
    </div>
</nav>
<div class='nc-tabs'>{tabs_html}</div>
""", unsafe_allow_html=True)

# Handle URL page param (works with the <a href> links above)
params = st.query_params
if "page" in params and params["page"] in ["detect", "news", "history", "about"]:
    if st.session_state["page"] != params["page"]:
        st.session_state["page"] = params["page"]
        st.rerun()
    page = params["page"]

# Theme toggle as a real button (top right via columns)
_, theme_col = st.columns([10, 1])
with theme_col:
    if st.button(theme_emoji, key="theme_toggle", type="secondary", use_container_width=True):
        st.session_state["dark_mode"] = not dark
        st.rerun()

# ── Content ────────────────────────────────────────────────
st.markdown("<div class='nc-content'>", unsafe_allow_html=True)

@st.cache_resource
def init_db():
    try:
        run_schema()
    except Exception:
        pass

init_db()

if page == "detect":
    detect.render()
elif page == "news":
    news.render()
elif page == "history":
    history.render()
elif page == "about":
    about.render()

st.markdown("</div>", unsafe_allow_html=True)
