import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
if "mobile_menu" not in st.session_state:
    st.session_state["mobile_menu"] = False

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
    padding:0 24px; display:flex; align-items:center;
    justify-content:space-between; height:60px; position:sticky; top:0; z-index:100;
    box-shadow:0 1px 8px rgba(0,0,0,{'0.3' if dark else '0.06'});
}}
.nc-brand {{ display:flex; align-items:center; gap:10px; text-decoration:none; }}
.nc-brand-icon {{
    width:34px; height:34px; background:{accent}; border-radius:9px;
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
}}
.nc-brand-name {{ font-size:18px; font-weight:800; color:{text}; letter-spacing:-0.5px; }}
.nc-brand-sub {{ font-size:11px; color:{sub}; line-height:1; }}
.nc-nav-links {{ display:flex; align-items:center; gap:4px; }}
.nc-nav-link {{
    display:flex; align-items:center; gap:6px; padding:7px 14px;
    border-radius:8px; font-size:13px; font-weight:500; color:{sub};
    cursor:pointer; border:none; background:transparent; transition:all 0.15s;
    text-decoration:none;
}}
.nc-nav-link:hover {{ background:{'#334155' if dark else '#f1f5f9'}; color:{text}; }}
.nc-nav-link.active {{ background:{accent}; color:white; font-weight:600; }}
.nc-nav-link img {{ width:16px; height:16px; object-fit:contain; }}
.nc-nav-link.active img {{ filter:{FW}; }}
.nc-nav-link:not(.active) img {{ filter:{F}; }}
.nc-nav-right {{ display:flex; align-items:center; gap:8px; }}
.nc-theme-btn {{
    width:34px; height:34px; border-radius:8px; border:1px solid {border};
    background:transparent; cursor:pointer; display:flex; align-items:center;
    justify-content:center; font-size:16px; color:{text};
    transition:background 0.15s;
}}
.nc-theme-btn:hover {{ background:{'#334155' if dark else '#f1f5f9'}; }}
.nc-hamburger {{
    display:none; width:34px; height:34px; border-radius:8px;
    border:1px solid {border}; background:transparent; cursor:pointer;
    align-items:center; justify-content:center; flex-direction:column; gap:4px;
}}
.nc-hamburger span {{
    display:block; width:18px; height:2px; background:{text}; border-radius:2px;
}}
.nc-mobile-menu {{
    display:none; position:fixed; top:60px; left:0; right:0; bottom:0;
    background:{card}; z-index:99; padding:16px;
    border-top:1px solid {border}; flex-direction:column; gap:4px;
}}
.nc-mobile-link {{
    display:flex; align-items:center; gap:12px; padding:14px 16px;
    border-radius:10px; font-size:15px; font-weight:500; color:{text};
    cursor:pointer; border:none; background:transparent; width:100%;
    text-align:left; transition:background 0.15s;
}}
.nc-mobile-link:hover {{ background:{'#334155' if dark else '#f1f5f9'}; }}
.nc-mobile-link.active {{ background:{accent}; color:white; }}
.nc-mobile-link img {{ width:20px; height:20px; object-fit:contain; }}
.nc-mobile-link.active img {{ filter:{FW}; }}
.nc-mobile-link:not(.active) img {{ filter:{F}; }}
.nc-content {{ padding:24px; max-width:1200px; margin:0 auto; }}

@media (max-width:768px) {{
    .nc-nav-links {{ display:none !important; }}
    .nc-hamburger {{ display:flex !important; }}
    .nc-content {{ padding:16px; }}
    .nc-brand-sub {{ display:none; }}
}}
</style>
""", unsafe_allow_html=True)

# ── Navbar ─────────────────────────────────────────────────
nav_items = [
    ("detect",  "https://cdn-icons-png.flaticon.com/128/681/681508.png",   "Detect"),
    ("news",    "https://cdn-icons-png.flaticon.com/128/11437/11437791.png", "News"),
    ("history", "https://cdn-icons-png.flaticon.com/128/8375/8375772.png",  "History"),
    ("about",   "https://cdn-icons-png.flaticon.com/128/17450/17450816.png","About"),
]

links_html = ""
for p, icon, label in nav_items:
    active_cls = "active" if page == p else ""
    links_html += f"""
    <button class='nc-nav-link {active_cls}' onclick="window.location.href='?page={p}'">
        <img src='{icon}'>{label}
    </button>"""

mobile_links_html = ""
for p, icon, label in nav_items:
    active_cls = "active" if page == p else ""
    mobile_links_html += f"""
    <button class='nc-mobile-link {active_cls}' onclick="window.location.href='?page={p}'">
        <img src='{icon}'>{label}
    </button>"""

theme_icon_url = "https://cdn-icons-png.flaticon.com/128/66275/66275.png" if dark else "https://cdn-icons-png.flaticon.com/128/39857/39857.png"

st.markdown(f"""
<nav class='nc-nav'>
    <div class='nc-brand'>
        <div class='nc-brand-icon'><img src='https://cdn-icons-png.flaticon.com/128/681/681508.png' style='width:22px;height:22px;object-fit:contain;filter:brightness(0) invert(1);'></div>
        <div>
            <div class='nc-brand-name'>NetConfirm</div>
            <div class='nc-brand-sub'>AI Fake News Detector</div>
        </div>
    </div>
    <div class='nc-nav-links'>{links_html}</div>
    <div class='nc-nav-right'>
        <button class='nc-theme-btn' id='theme-btn'><img src='{theme_icon_url}' style='width:18px;height:18px;object-fit:contain;filter:{"brightness(0) invert(1)" if dark else F};'></button>
        <button class='nc-hamburger' id='hamburger-btn'>
            <span></span><span></span><span></span>
        </button>
    </div>
</nav>
<div class='nc-mobile-menu' id='mobile-menu'>
    {mobile_links_html}
    <div style='margin-top:auto;padding-top:16px;border-top:1px solid {border};'>
        <button class='nc-mobile-link' id='mobile-theme-btn'><img src='{theme_icon_url}' style='width:20px;height:20px;object-fit:contain;filter:{F};margin-right:8px;'> {'Light Mode' if dark else 'Dark Mode'}</button>
    </div>
</div>
<script>
const hamburger = document.getElementById('hamburger-btn');
const mobileMenu = document.getElementById('mobile-menu');
const themeBtn = document.getElementById('theme-btn');
const mobileThemeBtn = document.getElementById('mobile-theme-btn');
if(hamburger) hamburger.addEventListener('click', () => {{
    mobileMenu.style.display = mobileMenu.style.display === 'flex' ? 'none' : 'flex';
}});
if(themeBtn) themeBtn.addEventListener('click', () => {{
    window.location.href = '?page={page}&theme=toggle';
}});
if(mobileThemeBtn) mobileThemeBtn.addEventListener('click', () => {{
    window.location.href = '?page={page}&theme=toggle';
}});
</script>
""", unsafe_allow_html=True)

# Handle URL params for navigation and theme
params = st.query_params
if "page" in params:
    new_page = params["page"]
    if new_page in ["detect", "news", "history", "about"]:
        st.session_state["page"] = new_page
        page = new_page
if "theme" in params and params["theme"] == "toggle":
    st.session_state["dark_mode"] = not dark
    st.query_params.clear()
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
