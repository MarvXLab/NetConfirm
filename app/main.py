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

nav_items = [
    ("detect",     "🔍", "Detect"),
    ("batch",      "📋", "Batch Scan"),
    ("trending",   "📈", "Trending"),
    ("reputation", "🌐", "Reputation"),
    ("api",        "⚡", "API"),
    ("news",       "📰", "News"),
    ("history",    "🕓", "History"),
    ("about",      "ℹ️",  "About"),
]

current_label = next((f"{e} {l}" for p, e, l in nav_items if p == page), "🔍 Detect")

# Build desktop tab links and mobile menu items
desktop_tabs = ""
mobile_items = ""
for p, emoji, label in nav_items:
    active = "active" if p == page else ""
    desktop_tabs += f"""
        <a class="nc-tab {active}" href="?nav={p}" onclick="navTo('{p}');return false;">
            {emoji} {label}
        </a>"""
    mobile_items += f"""
        <a class="nc-mob-item {active}" href="?nav={p}" onclick="navTo('{p}');return false;">
            <span class="nc-mob-emoji">{emoji}</span>
            <span class="nc-mob-label">{label}</span>
        </a>"""

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

/* ══════════════════════════════════════════
   NAVBAR
══════════════════════════════════════════ */
.nc-nav {{
    background: {card};
    border-bottom: 1px solid {border};
    padding: 0 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 1px 8px rgba(0,0,0,0.35);
}}
.nc-brand {{
    display: flex; align-items: center; gap: 10px; text-decoration: none;
}}
.nc-brand-icon {{
    width: 32px; height: 32px; background: {accent}; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.nc-brand-name {{ font-size: 16px; font-weight: 800; color: {text}; letter-spacing: -0.5px; }}
.nc-brand-sub  {{ font-size: 10px; color: {sub}; line-height: 1; }}

/* ── Desktop tab bar ── */
.nc-desktop-tabs {{
    background: {card};
    border-bottom: 1px solid {border};
    display: flex;
    align-items: center;
    padding: 0 8px;
    overflow-x: auto;
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
    gap: 2px;
}}
.nc-desktop-tabs::-webkit-scrollbar {{ display: none; }}
.nc-tab {{
    display: flex; align-items: center; gap: 6px;
    padding: 12px 14px;
    font-size: 13px; font-weight: 500;
    color: {sub};
    text-decoration: none;
    white-space: nowrap;
    border-bottom: 2px solid transparent;
    transition: color 0.15s, border-color 0.15s;
    cursor: pointer;
}}
.nc-tab:hover {{ color: {text}; }}
.nc-tab.active {{
    color: {text};
    border-bottom: 2px solid {text};
    font-weight: 700;
}}

/* ── Hamburger button (mobile only) ── */
.nc-ham-btn {{
    display: none;
    background: none;
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 10px;
    cursor: pointer;
    color: {text};
    font-size: 20px;
    line-height: 1;
    transition: background 0.15s;
}}
.nc-ham-btn:hover {{ background: {border}; }}

/* ── Mobile overlay menu ── */
.nc-mob-overlay {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 1001;
}}
.nc-mob-overlay.open {{ display: block; }}

.nc-mob-drawer {{
    position: fixed;
    top: 0; right: -280px;
    width: 260px; height: 100%;
    background: {card};
    border-left: 1px solid {border};
    z-index: 1002;
    transition: right 0.25s ease;
    display: flex; flex-direction: column;
    box-shadow: -4px 0 24px rgba(0,0,0,0.4);
}}
.nc-mob-drawer.open {{ right: 0; }}

.nc-mob-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 20px;
    border-bottom: 1px solid {border};
    flex-shrink: 0;
}}
.nc-mob-title {{ font-size: 15px; font-weight: 800; color: {text}; }}
.nc-mob-close {{
    background: none; border: none; cursor: pointer;
    color: {sub}; font-size: 22px; line-height: 1; padding: 4px;
    border-radius: 6px; transition: background 0.15s;
}}
.nc-mob-close:hover {{ background: {border}; color: {text}; }}

.nc-mob-nav {{
    flex: 1; overflow-y: auto; padding: 8px 0;
}}
.nc-mob-item {{
    display: flex; align-items: center; gap: 14px;
    padding: 14px 20px;
    font-size: 14px; font-weight: 500;
    color: {sub};
    text-decoration: none;
    border-left: 3px solid transparent;
    transition: all 0.15s;
    cursor: pointer;
}}
.nc-mob-item:hover {{ background: {border}33; color: {text}; }}
.nc-mob-item.active {{
    color: {text}; font-weight: 700;
    background: {accent}33;
    border-left: 3px solid {text};
}}
.nc-mob-emoji {{ font-size: 18px; width: 24px; text-align: center; flex-shrink: 0; }}
.nc-mob-label {{ font-size: 14px; }}

.nc-mob-footer {{
    padding: 16px 20px;
    border-top: 1px solid {border};
    font-size: 11px; color: {sub};
    flex-shrink: 0;
}}

/* ── Content ── */
.nc-content {{
    padding: 20px 20px 40px 20px;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
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
.nc-info-panel {{ display: block; }}

/* ══════════════════════════════════════════
   MOBILE BREAKPOINT
══════════════════════════════════════════ */
@media (max-width: 768px) {{
    .nc-desktop-tabs {{ display: none !important; }}
    .nc-ham-btn {{ display: block; }}
    .nc-brand-sub {{ display: none; }}
    .nc-content {{ padding: 14px 14px 32px 14px; }}
    .nc-info-panel {{ display: none; }}
    [data-testid="column"] {{
        width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
    }}
}}
@media (max-width: 480px) {{
    .nc-brand-name {{ font-size: 14px; }}
    .nc-content {{ padding: 12px 12px 28px 12px; }}
}}
</style>

<!-- ══ NAVBAR ══ -->
<nav class="nc-nav">
    <div class="nc-brand">
        <div class="nc-brand-icon">
            <img src="https://cdn-icons-png.flaticon.com/128/681/681508.png"
                style="width:18px;height:18px;object-fit:contain;filter:{FW};">
        </div>
        <div>
            <div class="nc-brand-name">NetConfirm</div>
            <div class="nc-brand-sub">AI Fake News Detector</div>
        </div>
    </div>
    <button class="nc-ham-btn" onclick="toggleMenu()" id="hamBtn" aria-label="Menu">☰</button>
</nav>

<!-- ══ DESKTOP TABS ══ -->
<div class="nc-desktop-tabs">
    {desktop_tabs}
</div>

<!-- ══ MOBILE OVERLAY ══ -->
<div class="nc-mob-overlay" id="mobOverlay" onclick="closeMenu()"></div>

<!-- ══ MOBILE DRAWER ══ -->
<div class="nc-mob-drawer" id="mobDrawer">
    <div class="nc-mob-header">
        <span class="nc-mob-title">NetConfirm</span>
        <button class="nc-mob-close" onclick="closeMenu()">✕</button>
    </div>
    <nav class="nc-mob-nav">
        {mobile_items}
    </nav>
    <div class="nc-mob-footer">AI Fake News Detector · v1.0</div>
</div>

<script>
function toggleMenu() {{
    var overlay = document.getElementById('mobOverlay');
    var drawer  = document.getElementById('mobDrawer');
    var btn     = document.getElementById('hamBtn');
    var isOpen  = drawer.classList.contains('open');
    if (isOpen) {{
        closeMenu();
    }} else {{
        overlay.classList.add('open');
        drawer.classList.add('open');
        btn.textContent = '✕';
        document.body.style.overflow = 'hidden';
    }}
}}

function closeMenu() {{
    var overlay = document.getElementById('mobOverlay');
    var drawer  = document.getElementById('mobDrawer');
    var btn     = document.getElementById('hamBtn');
    overlay.classList.remove('open');
    drawer.classList.remove('open');
    btn.textContent = '☰';
    document.body.style.overflow = '';
}}

function navTo(page) {{
    closeMenu();
    // Update URL param and trigger Streamlit rerun via query param
    var url = new URL(window.location.href);
    url.searchParams.set('nav', page);
    window.location.href = url.toString();
}}
</script>
""", unsafe_allow_html=True)

# Handle URL nav param
params = st.query_params
if "nav" in params:
    nav_val = params["nav"]
    valid   = [p for p, _, _ in nav_items]
    if nav_val in valid and nav_val != page:
        st.session_state["page"] = nav_val
        st.query_params.clear()
        st.rerun()
    elif nav_val in valid:
        st.query_params.clear()

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
