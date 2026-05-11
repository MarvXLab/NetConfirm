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
from app.tabs import detect, history, about, news, batch, trending, reputation, api_playground

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

/* ── Reset & base ── */
*, html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}}
div[data-testid="stAppViewContainer"] {{ background: {bg}; }}
div[data-testid="stHeader"] {{ display: none; }}
#MainMenu, footer, header {{ visibility: hidden; }}

/* Remove ALL Streamlit default padding */
.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}
section[data-testid="stSidebar"] {{ display: none; }}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {{
    border: 1px solid {border} !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    background: {card} !important;
    color: {text} !important;
    padding: 12px !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
    border-color: {accent} !important;
    box-shadow: 0 0 0 3px {accent}18 !important;
}}

/* ── Buttons ── */
.stButton > button[kind="primary"] {{
    background: {accent};
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    padding: 11px 24px;
    transition: all 0.15s;
    box-shadow: 0 2px 8px {accent}40;
    width: 100%;
}}
.stButton > button[kind="primary"]:hover {{
    background: #2d2d4e;
    transform: translateY(-1px);
}}
.stButton > button[kind="secondary"] {{
    background: {card};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    padding: 9px 18px;
    width: 100%;
}}

/* ── Metrics ── */
[data-testid="metric-container"] {{
    background: {card};
    border-radius: 10px;
    padding: 14px 16px;
    border: 1px solid {border};
}}
[data-testid="metric-container"] label,
[data-testid="metric-container"] div {{
    color: {text} !important;
}}

/* ── Misc ── */
.stSlider [data-baseweb="slider"] {{ padding-top: 6px; }}
.stNumberInput input {{ background: {card} !important; color: {text} !important; }}
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-thumb {{ background: {border}; border-radius: 3px; }}

/* ── Navbar ── */
.nc-nav {{
    background: {card};
    border-bottom: 1px solid {border};
    padding: 0 16px;
    display: flex;
    align-items: center;
    height: 56px;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 1px 8px rgba(0,0,0,0.3);
}}
.nc-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}}
.nc-brand-icon {{
    width: 32px;
    height: 32px;
    background: {accent};
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}
.nc-brand-name {{
    font-size: 16px;
    font-weight: 800;
    color: {text};
    letter-spacing: -0.5px;
    white-space: nowrap;
}}
.nc-brand-sub {{
    font-size: 10px;
    color: {sub};
    line-height: 1;
    white-space: nowrap;
}}

/* ── Tab nav ── */
.nc-tabs {{
    background: {card};
    border-bottom: 1px solid {border};
    display: flex;
    align-items: center;
    padding: 0 4px;
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
    gap: 0;
}}
.nc-tabs::-webkit-scrollbar {{ display: none; }}

/* Make nav buttons look like tabs */
.nc-tabs .stButton > button {{
    padding: 10px 12px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    color: {sub} !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    white-space: nowrap !important;
    box-shadow: none !important;
    min-width: fit-content !important;
    transition: color 0.15s !important;
}}
.nc-tabs .stButton > button:hover {{
    color: {text} !important;
    background: transparent !important;
    transform: none !important;
}}
.nc-tabs .stButton > button[kind="primary"] {{
    color: {text} !important;
    border-bottom: 2px solid {text} !important;
    background: transparent !important;
    box-shadow: none !important;
    font-weight: 700 !important;
}}

/* ── Content area ── */
.nc-content {{
    padding: 20px 16px 40px 16px;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}}

/* ── Responsive columns — stack on mobile ── */
@media (max-width: 768px) {{
    .nc-brand-sub {{ display: none; }}
    .nc-content {{ padding: 14px 12px 32px 12px; }}
    .nc-nav {{ padding: 0 12px; }}

    /* Stack Streamlit columns on mobile */
    [data-testid="column"] {{
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }}

    /* Smaller text on mobile */
    .stTextArea textarea, .stTextInput input {{
        font-size: 16px !important; /* prevents iOS zoom */
    }}
}}

@media (max-width: 480px) {{
    .nc-brand-name {{ font-size: 14px; }}
    .nc-tabs .stButton > button {{
        padding: 10px 8px !important;
        font-size: 11px !important;
    }}
    .nc-content {{ padding: 10px 10px 28px 10px; }}
}}

/* ── Global text colours ── */
p, span, label {{ color: {text}; }}
h1, h2, h3, h4, h5, h6 {{ color: {text} !important; }}
.stMarkdown p {{ color: {text}; }}
table {{ color: {text}; width: 100%; }}
thead tr th {{ color: {text} !important; background: {card} !important; }}
tbody tr td {{ color: {text} !important; background: {bg} !important; }}

/* ── Plotly charts responsive ── */
.js-plotly-plot, .plotly {{ width: 100% !important; }}

/* ── Download button ── */
.stDownloadButton > button {{
    background: {card} !important;
    color: {text} !important;
    border: 1px solid {border} !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    width: 100%;
}}

/* ── Tabs (st.tabs) ── */
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    gap: 4px;
    overflow-x: auto;
    flex-wrap: nowrap;
}}
.stTabs [data-baseweb="tab"] {{
    background: {card} !important;
    color: {sub} !important;
    border-radius: 8px 8px 0 0 !important;
    font-size: 13px !important;
    white-space: nowrap;
}}
.stTabs [aria-selected="true"] {{
    color: {text} !important;
    border-bottom: 2px solid {text} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: transparent !important;
    padding: 0 !important;
}}

/* ── Radio buttons ── */
.stRadio label {{ color: {text} !important; }}
.stRadio [data-testid="stMarkdownContainer"] p {{ color: {text} !important; }}

/* ── Select box ── */
.stSelectbox label {{ color: {text} !important; }}
[data-baseweb="select"] > div {{
    background: {card} !important;
    border-color: {border} !important;
    color: {text} !important;
}}

/* ── Checkbox ── */
.stCheckbox label {{ color: {text} !important; }}

/* ── Spinner ── */
.stSpinner > div {{ border-top-color: {text} !important; }}

/* ── Alerts ── */
.stAlert {{ border-radius: 8px !important; }}
</style>
""", unsafe_allow_html=True)

# ── Navbar ──────────────────────────────────────────────────
st.markdown(f"""
<nav class='nc-nav'>
    <div class='nc-brand'>
        <div class='nc-brand-icon'>
            <img src='https://cdn-icons-png.flaticon.com/128/681/681508.png'
                style='width:18px;height:18px;object-fit:contain;filter:{FW};'>
        </div>
        <div>
            <div class='nc-brand-name'>NetConfirm</div>
            <div class='nc-brand-sub'>AI Fake News Detector</div>
        </div>
    </div>
</nav>
""", unsafe_allow_html=True)

# ── Tab nav ──────────────────────────────────────────────────
nav_items = [
    ("detect",     "🔍 Detect"),
    ("batch",      "📋 Batch"),
    ("trending",   "📈 Trending"),
    ("reputation", "🌐 Reputation"),
    ("api",        "⚡ API"),
    ("news",       "📰 News"),
    ("history",    "🕓 History"),
    ("about",      "ℹ️ About"),
]

st.markdown("<div class='nc-tabs'>", unsafe_allow_html=True)
tab_cols = st.columns(len(nav_items))
for i, (p, label) in enumerate(nav_items):
    with tab_cols[i]:
        btn_type = "primary" if page == p else "secondary"
        if st.button(label, key=f"nav_{p}", type=btn_type, use_container_width=True):
            st.session_state["page"] = p
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ── Content ──────────────────────────────────────────────────
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
elif page == "api":
    api_playground.render()
elif page == "news":
    news.render()
elif page == "history":
    history.render()
elif page == "about":
    about.render()

st.markdown("</div>", unsafe_allow_html=True)
