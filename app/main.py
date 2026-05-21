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
if "menu_open" not in st.session_state:
    st.session_state["menu_open"] = False

page = st.session_state["page"]
menu_open = st.session_state["menu_open"]

bg     = "#0f172a"
card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
accent = "#1a1a2e"
FW     = "brightness(0) invert(1)"

nav_items = [
    ("detect",     "🔍", "Detect"),
    ("batch",      "📋", "Batch Scan"),
    ("trending",   "📈", "Trending"),
    ("reputation", "🌐", "Reputation"),
    ("api",        "⚡", "API"),
    ("news",       "📰", "News"),
    ("history",    "🕓", "History"),
    ("about",      "ℹ️", "About"),
]

# Current page label for mobile header
current_label = next((f"{e} {l}" for p, e, l in nav_items if p == page), "🔍 Detect")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}}
div[data-testid="stAppViewContainer"] {{ background: {bg}; }}
div[data-testid="stHeader"] {{ display: none; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 0 !important; max-width: 100% !important; }}
section[data-testid="stSidebar"] {{ display: none; }}

/* ── Inputs ── */
.stTextArea textarea, .stTextInput input {{
    border: 1px solid {border} !important; border-radius: 8px !important;
    font-size: 16px !important; background: {card} !important;
    color: {text} !important; padding: 12px !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
    border-color: {accent} !important; box-shadow: 0 0 0 3px {accent}18 !important;
}}

/* ── Buttons ── */
.stButton > button[kind="primary"] {{
    background: {accent}; color: white; border: none; border-radius: 8px;
    font-size: 14px; font-weight: 600; padding: 11px 24px;
    transition: all 0.15s; box-shadow: 0 2px 8px {accent}40; width: 100%;
}}
.stButton > button[kind="primary"]:hover {{ background: #2d2d4e; transform: translateY(-1px); }}
.stButton > button[kind="secondary"] {{
    background: {card}; color: {text}; border: 1px solid {border};
    border-radius: 8px; font-size: 13px; font-weight: 500; padding: 9px 18px; width: 100%;
}}

/* ── Metrics ── */
[data-testid="metric-container"] {{
    background: {card}; border-radius: 10px; padding: 14px 16px; border: 1px solid {border};
}}
[data-testid="metric-container"] label,
[data-testid="metric-container"] div {{ color: {text} !important; }}

/* ── Misc ── */
.stSlider [data-baseweb="slider"] {{ padding-top: 6px; }}
.stNumberInput input {{ background: {card} !important; color: {text} !important; }}
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-thumb {{ background: {border}; border-radius: 3px; }}

/* ── Navbar ── */
.nc-nav {{
    background: {card}; border-bottom: 1px solid {border};
    padding: 0 16px; display: flex; align-items: center;
    justify-content: space-between;
    height: 56px; position: sticky; top: 0; z-index: 999;
    box-shadow: 0 1px 8px rgba(0,0,0,0.3);
}}
.nc-brand {{ display: flex; align-items: center; gap: 10px; flex-shrink: 0; }}
.nc-brand-icon {{
    width: 32px; height: 32px; background: {accent}; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.nc-brand-name {{ font-size: 16px; font-weight: 800; color: {text}; letter-spacing: -0.5px; }}
.nc-brand-sub  {{ font-size: 10px; color: {sub}; line-height: 1; }}
.nc-current-page {{
    font-size: 13px; font-weight: 600; color: {sub};
    display: none;
}}

/* ── Desktop tab bar ── */
.nc-tabs {{
    background: {card}; border-bottom: 1px solid {border};
    display: flex; align-items: center; padding: 0 4px;
    overflow-x: auto; overflow-y: hidden;
    scrollbar-width: none; -webkit-overflow-scrolling: touch;
}}
.nc-tabs::-webkit-scrollbar {{ display: none; }}
.nc-tabs .stButton > button {{
    padding: 10px 14px !important; font-size: 13px !important; font-weight: 500 !important;
    color: {sub} !important; background: transparent !important; border: none !important;
    border-bottom: 2px solid transparent !important; border-radius: 0 !important;
    white-space: nowrap !important; box-shadow: none !important;
    min-width: fit-content !important; transition: color 0.15s !important;
}}
.nc-tabs .stButton > button:hover {{ color: {text} !important; background: transparent !important; transform: none !important; }}
.nc-tabs .stButton > button[kind="primary"] {{
    color: {text} !important; border-bottom: 2px solid {text} !important;
    background: transparent !important; box-shadow: none !important; font-weight: 700 !important;
}}

/* ── Hamburger button ── */
.nc-hamburger {{ display: none; }}
.nc-hamburger .stButton > button {{
    background: transparent !important; border: 1px solid {border} !important;
    border-radius: 8px !important; padding: 6px 10px !important;
    font-size: 18px !important; color: {text} !important;
    box-shadow: none !important; width: auto !important;
    min-width: 40px !important; line-height: 1 !important;
}}
.nc-hamburger .stButton > button:hover {{ background: {border} !important; transform: none !important; }}

/* ── Mobile dropdown menu ── */
.nc-mobile-menu {{
    display: none;
    position: fixed; top: 56px; left: 0; right: 0;
    background: {card}; border-bottom: 1px solid {border};
    z-index: 998; padding: 8px 0;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}}
.nc-mobile-menu.open {{ display: block; }}
.nc-mobile-menu .stButton > button {{
    background: transparent !important; border: none !important;
    border-radius: 0 !important; padding: 12px 20px !important;
    font-size: 14px !important; font-weight: 500 !important;
    color: {sub} !important; text-align: left !important;
    width: 100% !important; box-shadow: none !important;
    border-bottom: 1px solid {border}22 !important;
    justify-content: flex-start !important;
}}
.nc-mobile-menu .stButton > button:hover {{
    background: {border}44 !important; color: {text} !important; transform: none !important;
}}
.nc-mobile-menu .stButton > button[kind="primary"] {{
    background: {accent}22 !important; color: {text} !important;
    border-left: 3px solid {text} !important; font-weight: 700 !important;
}}

/* ── Content ── */
.nc-content {{
    padding: 20px 20px 40px 20px; max-width: 1200px; margin: 0 auto; width: 100%;
}}

/* ── Global text ── */
p, span, label {{ color: {text}; }}
h1, h2, h3, h4, h5, h6 {{ color: {text} !important; }}
.stMarkdown p {{ color: {text}; }}
table {{ color: {text}; width: 100%; }}
thead tr th {{ color: {text} !important; background: {card} !important; }}
tbody tr td {{ color: {text} !important; background: {bg} !important; }}
.js-plotly-plot, .plotly {{ width: 100% !important; }}
.stDownloadButton > button {{
    background: {card} !important; color: {text} !important;
    border: 1px solid {border} !important; border-radius: 8px !important;
    font-size: 13px !important; width: 100%;
}}
.stTabs [data-baseweb="tab-list"] {{
    background: transparent !important; gap: 4px; overflow-x: auto; flex-wrap: nowrap;
}}
.stTabs [data-baseweb="tab"] {{
    background: {card} !important; color: {sub} !important;
    border-radius: 8px 8px 0 0 !important; font-size: 13px !important; white-space: nowrap;
}}
.stTabs [aria-selected="true"] {{ color: {text} !important; border-bottom: 2px solid {text} !important; }}
.stTabs [data-baseweb="tab-panel"] {{ background: transparent !important; padding: 0 !important; }}
.stRadio label {{ color: {text} !important; }}
.stRadio [data-testid="stMarkdownContainer"] p {{ color: {text} !important; }}
.stSelectbox label {{ color: {text} !important; }}
[data-baseweb="select"] > div {{ background: {card} !important; border-color: {border} !important; color: {text} !important; }}
.stCheckbox label {{ color: {text} !important; }}
.stAlert {{ border-radius: 8px !important; }}

/* ── MOBILE: hide desktop tabs, show hamburger ── */
@media (max-width: 768px) {{
    .nc-tabs {{ display: none !important; }}
    .nc-hamburger {{ display: block; }}
    .nc-brand-sub {{ display: none; }}
    .nc-current-page {{ display: block; }}
    .nc-content {{ padding: 14px 14px 32px 14px; }}

    /* Stack columns */
    [data-testid="column"] {{
        width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
    }}
}}

@media (max-width: 480px) {{
    .nc-brand-name {{ font-size: 14px; }}
    .nc-content {{ padding: 12px 12px 28px 12px; }}
}}
</style>
""", unsafe_allow_html=True)

# ── Navbar ───────────────────────────────────────────────────
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
    <div class='nc-current-page'>{current_label}</div>
</nav>
""", unsafe_allow_html=True)

# ── Desktop tab bar ──────────────────────────────────────────
st.markdown("<div class='nc-tabs'>", unsafe_allow_html=True)
tab_cols = st.columns(len(nav_items))
for i, (p, emoji, label) in enumerate(nav_items):
    with tab_cols[i]:
        btn_type = "primary" if page == p else "secondary"
        if st.button(f"{emoji} {label}", key=f"nav_{p}", type=btn_type, use_container_width=True):
            st.session_state["page"] = p
            st.session_state["menu_open"] = False
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ── Mobile hamburger button ──────────────────────────────────
st.markdown("<div class='nc-hamburger'>", unsafe_allow_html=True)
ham_col, _ = st.columns([1, 8])
with ham_col:
    ham_icon = "✕" if menu_open else "☰"
    if st.button(ham_icon, key="hamburger", type="secondary"):
        st.session_state["menu_open"] = not menu_open
        st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ── Mobile dropdown menu ─────────────────────────────────────
menu_class = "nc-mobile-menu open" if menu_open else "nc-mobile-menu"
st.markdown(f"<div class='{menu_class}'>", unsafe_allow_html=True)
if menu_open:
    for p, emoji, label in nav_items:
        btn_type = "primary" if page == p else "secondary"
        if st.button(f"{emoji}  {label}", key=f"mob_{p}", type=btn_type, use_container_width=True):
            st.session_state["page"] = p
            st.session_state["menu_open"] = False
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
