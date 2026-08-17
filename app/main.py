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

# Check query params early so page is correct before rendering nav
_early_params = st.query_params
if "news_cat" in _early_params and "nav" not in _early_params:
    st.session_state["page"] = "news"

page   = st.session_state["page"]
bg     = "#0f172a"
card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
accent = "#1a1a2e"
FW     = "brightness(0) invert(1)"

NAV_ICONS = {
    "detect":     "https://cdn-icons-png.flaticon.com/128/10496/10496548.png",
    "batch":      "https://cdn-icons-png.flaticon.com/128/4240/4240759.png",
    "trending":   "https://cdn-icons-png.flaticon.com/128/12513/12513740.png",
    "reputation": "https://cdn-icons-png.flaticon.com/128/8915/8915911.png",
    "api":        "https://cdn-icons-png.flaticon.com/128/8267/8267389.png",
    "news":       "https://cdn-icons-png.flaticon.com/128/2963/2963907.png",
    "history":    "https://cdn-icons-png.flaticon.com/128/6619/6619116.png",
    "about":      "https://cdn-icons-png.flaticon.com/128/6811/6811518.png",
}

nav_items = [
    ("detect",     "Detect"),
    ("batch",      "Batch Scan"),
    ("trending",   "Trending"),
    ("reputation", "Reputation"),
    ("api",        "API"),
    ("news",       "News"),
    ("history",    "History"),
    ("about",      "About"),
]

# Build tab links — image icons, no emoji, plain href (same-tab navigation)
tab_links = ""
for p, label in nav_items:
    active = "active" if p == page else ""
    icon_url = NAV_ICONS[p]
    tab_links += (
        f'<a class="nc-tab {active}" href="?nav={p}" target="_self">'
        f'<img src="{icon_url}" style="width:16px;height:16px;object-fit:contain;filter:brightness(0) invert(1);flex-shrink:0;">'
        f'{label}</a>'
    )

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
    font-size: 12px; font-weight: 400;
    color: rgba(255,255,255,0.55);
    text-decoration: none;
    white-space: nowrap;
    border-bottom: 2px solid transparent;
    transition: color 0.15s, border-color 0.15s;
    cursor: pointer;
    letter-spacing: 0.2px;
}}
.nc-tab:hover {{ color: rgba(255,255,255,0.85); }}
.nc-tab.active {{
    color: #ffffff;
    border-bottom: 2px solid #ffffff;
    font-weight: 600;
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
    .nc-brand-sub {{ display: none; }}
    .nc-content {{ padding: 14px 14px 32px 14px; }}
    .nc-info-panel {{ display: none; }}
    [data-testid="column"] {{
        width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
    }}
}}
@media (max-width: 480px) {{
    .nc-brand-name {{ font-size: 14px; }}
    .nc-tab {{ padding: 10px 10px; font-size: 12px; }}
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
</nav>

<!-- ══ TAB BAR (scrollable on mobile + desktop) ══ -->
<div class="nc-desktop-tabs">
    {tab_links}
</div>
""", unsafe_allow_html=True)

# ── Ownership Disclaimer ─────────────────────────────────────────────────────
if "disclaimer_accepted" not in st.session_state:
    st.session_state["disclaimer_accepted"] = False

if not st.session_state["disclaimer_accepted"]:
    st.markdown("""
    <style>
    #disclaimer-overlay {
        position: fixed; inset: 0; z-index: 999999;
        background: rgba(0,0,0,0.96); backdrop-filter: blur(10px);
        display: flex; align-items: flex-start; justify-content: center;
        padding: 16px; font-family: 'Inter', sans-serif;
        overflow-y: auto;
    }
    #disclaimer-box {
        background: #0f172a; border: 1px solid #334155;
        border-radius: 20px; max-width: 540px; width: 100%;
        box-shadow: 0 32px 80px rgba(0,0,0,0.7); overflow: hidden;
        margin: auto;
    }
    #disclaimer-header {
        background: linear-gradient(135deg,rgba(239,68,68,0.15),rgba(239,68,68,0.05));
        border-bottom: 1px solid rgba(239,68,68,0.2);
        padding: 20px 24px; display: flex; align-items: center; gap: 14px;
    }
    #disclaimer-icon {
        width: 44px; height: 44px; border-radius: 12px;
        background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3);
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
        font-size: 22px;
    }
    #disclaimer-title { font-size: 17px; font-weight: 700; color: #f1f5f9; margin: 0; }
    #disclaimer-sub   { font-size: 12px; color: #64748b; margin: 3px 0 0; }
    #disclaimer-body  { padding: 20px 24px; display: flex; flex-direction: column; gap: 14px; }
    .d-alert {
        background: rgba(239,68,68,0.07); border: 1px solid rgba(239,68,68,0.2);
        border-radius: 10px; padding: 12px 16px;
        font-size: 13px; color: #fca5a5; line-height: 1.6; font-weight: 600;
    }
    .d-text { font-size: 13px; color: #94a3b8; line-height: 1.75; margin: 0; }
    .d-contact {
        background: #1e293b; border: 1px solid #334155;
        border-radius: 10px; padding: 14px 16px;
    }
    .d-contact-label {
        font-size: 10px; font-weight: 700; color: #475569;
        text-transform: uppercase; letter-spacing: 0.7px; margin: 0 0 10px;
    }
    .d-contact a {
        display: flex; align-items: center; gap: 8px;
        color: #818cf8; font-size: 13px; text-decoration: none;
        font-weight: 500; margin-bottom: 6px;
    }
    .d-contact a:last-child { margin-bottom: 0; }
    .d-contact a:hover { color: #a5b4fc; }
    .d-contact svg { flex-shrink: 0; }
    .d-divider { border: none; border-top: 1px solid #1e293b; margin: 0; }
    .d-terms {
        background: #0a0f1a; border: 1px solid #1e293b;
        border-radius: 10px; padding: 14px 16px;
    }
    .d-terms-label {
        font-size: 10px; font-weight: 700; color: #475569;
        text-transform: uppercase; letter-spacing: 0.7px; margin: 0 0 10px;
    }
    .d-terms p { font-size: 12px; color: #64748b; line-height: 1.7; margin: 0 0 8px; }
    .d-terms p:last-child { margin: 0; }
    .d-note { font-size: 11px; color: #475569; text-align: center; line-height: 1.6; margin: 0; }
    .d-copyright { font-size: 11px; color: #334155; text-align: center; margin: 0; }
    @media (max-width: 480px) {
        #disclaimer-overlay { padding: 12px; align-items: flex-start; }
        #disclaimer-header { padding: 16px 18px; }
        #disclaimer-body { padding: 16px 18px; gap: 12px; }
        #disclaimer-title { font-size: 15px; }
    }
    </style>

    <div id="disclaimer-overlay">
      <div id="disclaimer-box">
        <div id="disclaimer-header">
          <div id="disclaimer-icon">⚖️</div>
          <div>
            <p id="disclaimer-title">Intellectual Property Notice</p>
            <p id="disclaimer-sub">Please read carefully before continuing</p>
          </div>
        </div>
        <div id="disclaimer-body">
          <div class="d-alert">⚠️ OWNERSHIP DISCLAIMER</div>
          <p class="d-text">
            This application <strong style="color:#e2e8f0">NetConfirm AI Fake News Detector</strong>
            including its design, source code, machine learning models, database architecture,
            browser extension, and all associated intellectual property, was
            <strong style="color:#e2e8f0">solely conceived, designed, and built</strong>
            by its original developer. NOT TAIWO EMMANUEL WHO STOLE THIS PROJECT.
          </p>
          <p class="d-text">
            Any unauthorized reproduction, redistribution, reselling, or false claiming of
            ownership of this project or any part thereof is a violation of intellectual
            property rights and may be subject to legal action.
          </p>
          <p class="d-text">
            All rights reserved. Unauthorized use of this platform's branding, codebase,
            or infrastructure without explicit written permission from the original
            developer is strictly prohibited.
          </p>
          <div class="d-contact">
            <p class="d-contact-label">Contact Original Developer</p>
            <a href="mailto:marvxlab@gmail.com">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M20 4H4C2.9 4 2 4.9 2 6v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" fill="#EA4335"/>
              </svg>
              marvxlab@gmail.com
            </a>
            <a href="https://github.com/marvxlab" target="_blank">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="#f1f5f9">
                <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.009-.868-.013-1.703-2.782.604-3.369-1.342-3.369-1.342-.454-1.154-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836a9.59 9.59 0 012.504.337c1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
              </svg>
              github.com/marvxlab
            </a>
            <a href="tel:+2348153774727">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M6.62 10.79a15.053 15.053 0 006.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z" fill="#34A853"/>
              </svg>
              +234 815 377 4727
            </a>
          </div>
          <p class="d-copyright">
            &copy; 2025 MarvXLab &nbsp;&middot;&nbsp;
            <span id="tc-trigger" onclick="document.getElementById('tc-modal').style.display='flex'"
              style="color:#818cf8;cursor:pointer;text-decoration:underline;font-size:11px;">Terms &amp; Conditions</span>
          </p>

          <!-- T&C Modal -->
          <div id="tc-modal" style="display:none;position:fixed;inset:0;z-index:9999999;background:rgba(0,0,0,0.85);backdrop-filter:blur(6px);align-items:center;justify-content:center;padding:16px;overflow-y:auto;">
            <div style="background:#0f172a;border:1px solid #334155;border-radius:16px;max-width:500px;width:100%;max-height:85vh;overflow-y:auto;padding:24px;position:relative;margin:auto;">
              <button onclick="document.getElementById('tc-modal').style.display='none'" style="position:absolute;top:14px;right:16px;background:none;border:none;color:#64748b;font-size:20px;cursor:pointer;line-height:1;">&times;</button>
              <p style="font-size:15px;font-weight:700;color:#f1f5f9;margin:0 0 4px;">Terms &amp; Conditions</p>
              <p style="font-size:11px;color:#475569;margin:0 0 18px;">Effective Date: January 1, 2025 &nbsp;&middot;&nbsp; &copy; 2025 MarvXLab</p>

              <p style="font-size:12px;font-weight:600;color:#94a3b8;margin:0 0 6px;">1. Acceptance of Terms</p>
              <p style="font-size:12px;color:#64748b;line-height:1.7;margin:0 0 14px;">By accessing or using NetConfirm, you agree to be bound by these Terms and Conditions. If you do not agree, you must not use this platform.</p>

              <p style="font-size:12px;font-weight:600;color:#94a3b8;margin:0 0 6px;">2. Intellectual Property</p>
              <p style="font-size:12px;color:#64748b;line-height:1.7;margin:0 0 14px;">All content, source code, machine learning models, UI designs, database architecture, and the browser extension are the exclusive intellectual property of MarvXLab. No part of this platform may be reproduced, distributed, or claimed as your own without explicit written permission from MarvXLab.</p>

              <p style="font-size:12px;font-weight:600;color:#94a3b8;margin:0 0 6px;">3. Permitted Use</p>
              <p style="font-size:12px;color:#64748b;line-height:1.7;margin:0 0 14px;">NetConfirm is provided for personal, non-commercial, informational use only. You may not use this platform to process content for commercial redistribution, automated scraping, or any purpose that violates applicable law.</p>

              <p style="font-size:12px;font-weight:600;color:#94a3b8;margin:0 0 6px;">4. Disclaimer of Warranties</p>
              <p style="font-size:12px;color:#64748b;line-height:1.7;margin:0 0 14px;">NetConfirm's AI predictions are provided for informational purposes only and do not constitute professional fact-checking, legal advice, or journalistic verification. MarvXLab makes no warranties, express or implied, regarding the accuracy or completeness of any prediction.</p>

              <p style="font-size:12px;font-weight:600;color:#94a3b8;margin:0 0 6px;">5. Prohibited Conduct</p>
              <p style="font-size:12px;color:#64748b;line-height:1.7;margin:0 0 14px;">You agree not to: attempt to reverse-engineer or decompile any part of the platform; claim ownership or authorship of this project; use the platform to spread misinformation; or interfere with the platform's infrastructure or security.</p>

              <p style="font-size:12px;font-weight:600;color:#94a3b8;margin:0 0 6px;">6. Limitation of Liability</p>
              <p style="font-size:12px;color:#64748b;line-height:1.7;margin:0 0 14px;">MarvXLab shall not be liable for any direct, indirect, incidental, or consequential damages arising from your use of or inability to use this platform.</p>

              <p style="font-size:12px;font-weight:600;color:#94a3b8;margin:0 0 6px;">7. Modifications</p>
              <p style="font-size:12px;color:#64748b;line-height:1.7;margin:0 0 14px;">MarvXLab reserves the right to modify, suspend, or discontinue the service at any time without prior notice. Continued use of the platform after any changes constitutes acceptance of the updated terms.</p>

              <p style="font-size:12px;font-weight:600;color:#94a3b8;margin:0 0 6px;">8. Contact</p>
              <p style="font-size:12px;color:#64748b;line-height:1.7;margin:0;">For inquiries regarding these terms, contact: <a href="mailto:marvxlab@gmail.com" style="color:#818cf8;">marvxlab@gmail.com</a></p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <script>
        history.pushState(null, '', window.location.href);
        window.addEventListener('popstate', function() {
            history.pushState(null, '', window.location.href);
        });
    </script>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:60vh'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅  I Understand & Continue", type="primary", use_container_width=True):
            st.session_state["disclaimer_accepted"] = True
            st.rerun()
    st.stop()

# ── End Disclaimer ────────────────────────────────────────────────────────────



if "nav" in params:
    nav_val = params["nav"]
    valid   = [p for p, _ in nav_items]
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
