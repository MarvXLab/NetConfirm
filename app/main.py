import sys
import os
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
from app.tabs import detect, history, about, news, batch, trending, reputation

st.set_page_config(
    page_title="NetConfirm — Fake News Detector",
    page_icon="https://cdn-icons-png.flaticon.com/128/681/681508.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "page" not in st.session_state:
    st.session_state["page"] = "detect"

page   = st.session_state["page"]
bg     = "#0f172a"
card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
accent = "#1a1a2e"
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
[data-testid="metric-container"] label, [data-testid="metric-container"] div {{
    color:{text} !important;
}}
.stSlider [data-baseweb="slider"] {{ padding-top:6px; }}
.stNumberInput input {{ background:{card} !important; color:{text} !important; }}
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-thumb {{ background:{border}; border-radius:3px; }}

/* Navbar */
.nc-nav {{
    background:{card}; border-bottom:1px solid {border};
    padding:0 16px; display:flex; align-items:center;
    height:60px; position:sticky; top:0; z-index:100;
    box-shadow:0 1px 8px rgba(0,0,0,0.3);
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
    display:flex; align-items:center; gap:2px; padding:0 8px;
    overflow-x:auto; scrollbar-width:none;
}}
.nc-tabs::-webkit-scrollbar {{ display:none; }}

/* Override Streamlit tab-button styling */
.nc-tabs .stButton > button {{
    display:flex !important; align-items:center !important; gap:6px !important;
    padding:12px 16px !important; font-size:13px !important; font-weight:500 !important;
    color:{sub} !important; cursor:pointer !important; border:none !important;
    background:transparent !important; white-space:nowrap !important;
    border-bottom:2px solid transparent !important; border-radius:0 !important;
    transition:all 0.15s !important; box-shadow:none !important;
}}
.nc-tabs .stButton > button:hover {{ color:{text} !important; }}

.nc-content {{ padding:24px; max-width:1200px; margin:0 auto; }}
@media (max-width:640px) {{ .nc-content {{ padding:12px; }} .nc-brand-sub {{ display:none; }} }}

/* Global text color overrides for dark mode */
p, span, label, div {{ color:{text}; }}
h1, h2, h3, h4, h5, h6 {{ color:{text} !important; }}
.stMarkdown p {{ color:{text}; }}
table {{ color:{text}; }}
thead tr th {{ color:{text} !important; background:{card} !important; }}
tbody tr td {{ color:{text} !important; background:{bg} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Navbar brand ────────────────────────────────────────────
st.markdown(f"""
<nav class='nc-nav'>
    <div class='nc-brand'>
        <div class='nc-brand-icon'>
            <img src='https://cdn-icons-png.flaticon.com/128/681/681508.png'
                style='width:20px;height:20px;object-fit:contain;filter:{FW};'>
        </div>
        <div>
            <div class='nc-brand-name'>NetConfirm</div>
            <div class='nc-brand-sub'>AI Fake News Detector</div>
        </div>
    </div>
</nav>
""", unsafe_allow_html=True)

# ── Tab nav using Streamlit buttons (no new-tab issue) ──────
nav_items = [
    ("detect",     "https://cdn-icons-png.flaticon.com/128/681/681508.png",    "🔍 Detect"),
    ("batch",      "https://cdn-icons-png.flaticon.com/128/9496/9496543.png",   "📋 Batch Scan"),
    ("trending",   "https://cdn-icons-png.flaticon.com/128/3281/3281289.png",   "📈 Trending"),
    ("reputation", "https://cdn-icons-png.flaticon.com/128/2910/2910791.png",   "🌐 Reputation"),
    ("news",       "https://cdn-icons-png.flaticon.com/128/11437/11437791.png", "📰 News"),
    ("history",    "https://cdn-icons-png.flaticon.com/128/8375/8375772.png",   "🕓 History"),
    ("about",      "https://cdn-icons-png.flaticon.com/128/17450/17450816.png", "ℹ️ About"),
]

st.markdown("<div class='nc-tabs'>", unsafe_allow_html=True)
tab_cols = st.columns(len(nav_items))
for i, (p, icon, label) in enumerate(nav_items):
    with tab_cols[i]:
        btn_type = "primary" if page == p else "secondary"
        if st.button(label, key=f"nav_{p}", type=btn_type, use_container_width=True):
            st.session_state["page"] = p
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ── Content ─────────────────────────────────────────────────
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
elif page == "batch":
    batch.render()
elif page == "trending":
    trending.render()
elif page == "reputation":
    reputation.render()
elif page == "news":
    news.render()
elif page == "history":
    history.render()
elif page == "about":
    about.render()

st.markdown("</div>", unsafe_allow_html=True)
