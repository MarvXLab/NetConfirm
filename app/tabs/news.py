import streamlit as st
import requests
import os
from datetime import datetime

CATEGORIES = ["General", "Technology", "Politics", "Business", "Entertainment", "Sports", "Science", "Health"]

card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
muted  = "#162032"
red    = "#dc2626"
green  = "#16a34a"


def get_api_key():
    key = os.getenv("NEWSAPI_KEY", "")
    if not key:
        try:
            key = st.secrets["newsapi"]["key"]
        except Exception:
            pass
    return key


def fetch_news(category="general", page_size=12):
    try:
        api_key = get_api_key()
        if not api_key:
            return None, "missing_key"
        url = "https://newsapi.org/v2/top-headlines"
        params = {"category": category.lower(), "language": "en",
                  "pageSize": page_size, "apiKey": api_key}
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        if data.get("status") == "ok":
            return data.get("articles", []), None
        return None, data.get("message", "fetch_error")
    except Exception:
        return None, "fetch_error"


def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return ""


def render():
    st.markdown(f"""
    <style>
    /* News hero */
    .nc-news-hero {{
        border-radius: 14px; overflow: hidden; margin-bottom: 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4); background: {card};
        border: 1px solid {border};
    }}
    .nc-news-hero img {{
        width: 100%; height: 260px; object-fit: cover; display: block;
    }}
    .nc-hero-body {{ padding: 16px 20px 20px 20px; background: {card}; }}
    .nc-hero-tag {{
        display: inline-block; background: {red}; color: white;
        font-size: 11px; font-weight: 700; padding: 3px 12px;
        border-radius: 20px; margin-bottom: 10px;
    }}
    .nc-hero-title {{
        font-size: 18px; font-weight: 800; color: {text};
        line-height: 1.35; margin: 0 0 8px 0;
    }}
    .nc-hero-meta {{ font-size: 12px; color: {sub}; margin: 0; }}

    /* News card */
    .nc-card {{
        background: {card}; border-radius: 12px; overflow: hidden;
        border: 1px solid {border}; transition: transform 0.15s;
        margin-bottom: 14px;
    }}
    .nc-card:hover {{ transform: translateY(-2px); }}
    .nc-card img {{ width: 100%; height: 140px; object-fit: cover; display: block; }}
    .nc-card-body {{ padding: 12px 14px 14px 14px; background: {card}; }}
    .nc-card-tag {{
        display: inline-block; background: {red}; color: white;
        font-size: 10px; font-weight: 700; padding: 2px 8px;
        border-radius: 20px; margin-bottom: 8px;
    }}
    .nc-card-title {{
        font-size: 13px; font-weight: 700; color: {text};
        line-height: 1.4; margin: 0;
    }}
    .nc-card-meta {{ font-size: 11px; color: {sub}; margin-top: 6px; }}

    /* List item */
    .nc-list-item {{
        background: {card}; border-radius: 10px; padding: 14px 16px;
        margin-bottom: 8px; border-left: 3px solid {green};
        border: 1px solid {border}; border-left: 3px solid {green};
    }}
    .nc-list-title {{
        font-size: 14px; font-weight: 600; color: {text};
        margin: 0 0 4px 0; line-height: 1.4;
    }}
    .nc-list-meta {{ font-size: 11px; color: {sub}; margin: 0; }}

    /* Ticker */
    .nc-ticker {{
        background: {muted}; border-radius: 8px; padding: 10px 16px;
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 16px; border: 1px solid {border};
        overflow: hidden;
    }}
    .nc-ticker-badge {{
        background: {red}; color: white; font-size: 10px; font-weight: 700;
        padding: 3px 10px; border-radius: 4px; white-space: nowrap; flex-shrink: 0;
    }}
    .nc-ticker-text {{
        font-size: 12px; color: {sub};
        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}

    /* Section header */
    .nc-section {{
        font-size: 16px; font-weight: 800; color: {text};
        margin: 20px 0 12px 0; padding-bottom: 8px;
        border-bottom: 2px solid {border};
    }}

    /* Mobile: single column grid */
    @media (max-width: 768px) {{
        .nc-news-hero img {{ height: 180px; }}
        .nc-hero-title {{ font-size: 15px; }}
        .nc-card img {{ height: 120px; }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # Header row
    today = datetime.now().strftime("%A, %B %d, %Y")
    col_h, col_d = st.columns([3, 1])
    with col_h:
        st.markdown(f"<p style='font-size:13px;color:{sub};margin:0;'>{today}</p>",
                    unsafe_allow_html=True)
    with col_d:
        st.markdown(f"<p style='font-size:12px;color:{sub};text-align:right;margin:0;"
                    f"font-weight:600;'>Verified News Feed</p>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Category selector — 4 per row on mobile
    selected_cat = st.session_state.get("news_category", "General")
    cols = st.columns(4)
    for i, cat in enumerate(CATEGORIES):
        with cols[i % 4]:
            if st.button(cat, key=f"nc_{cat}", use_container_width=True,
                         type="primary" if cat == selected_cat else "secondary"):
                st.session_state["news_category"] = cat
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    with st.spinner(""):
        articles, error = fetch_news(selected_cat)

    if error == "missing_key":
        st.markdown(f"""
        <div style='background:{muted};border:1px solid {border};border-radius:12px;
            padding:32px;text-align:center;'>
            <p style='font-size:32px;margin:0 0 12px 0;'>📰</p>
            <p style='font-size:16px;font-weight:700;color:{text};margin:0 0 6px 0;'>
                News Feed Setup Required</p>
            <p style='font-size:13px;color:{sub};margin:0;'>
                Add your NEWSAPI_KEY environment variable in Render to enable live news.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    if error or not articles:
        st.markdown(f"""
        <div style='background:{muted};border:1px solid {border};border-radius:12px;
            padding:32px;text-align:center;'>
            <p style='font-size:32px;margin:0 0 12px 0;'>📡</p>
            <p style='font-size:16px;font-weight:700;color:{text};margin:0 0 6px 0;'>
                Could not load news</p>
            <p style='font-size:13px;color:{sub};margin:0;'>Please try again later.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    with_img = [a for a in articles if a.get("urlToImage")]
    rest      = [a for a in articles if not a.get("urlToImage")]
    all_articles = with_img + rest

    # Ticker
    headlines = " · ".join([a["title"] for a in all_articles[:4] if a.get("title")])
    st.markdown(f"""
    <div class='nc-ticker'>
        <span class='nc-ticker-badge'>LIVE</span>
        <span class='nc-ticker-text'>{headlines}</span>
    </div>
    """, unsafe_allow_html=True)

    # Hero article
    if all_articles:
        h = all_articles[0]
        img_html = (f"<img src='{h.get('urlToImage','')}' "
                    f"onerror=\"this.style.display='none'\">") if h.get("urlToImage") else ""
        src  = h.get("source", {}).get("name", "") or selected_cat
        desc = (h.get("description") or "")[:120]
        st.markdown(f"""
        <a href='{h.get("url","#")}' target='_blank' style='text-decoration:none;'>
        <div class='nc-news-hero'>
            {img_html}
            <div class='nc-hero-body'>
                <span class='nc-hero-tag'>{src}</span>
                <p class='nc-hero-title'>{h.get("title","")}</p>
                <p class='nc-hero-meta'>{format_date(h.get("publishedAt",""))} · {desc}</p>
            </div>
        </div></a>
        """, unsafe_allow_html=True)

    # Grid — 3 cols desktop, 2 cols tablet (handled by Streamlit columns)
    st.markdown(f"<div class='nc-section'>Highlight News</div>", unsafe_allow_html=True)
    grid = all_articles[1:7]
    if grid:
        c1, c2, c3 = st.columns(3)
        for i, a in enumerate(grid):
            with [c1, c2, c3][i % 3]:
                img_html = (f"<img src='{a.get('urlToImage','')}' "
                            f"onerror=\"this.style.display='none'\">") if a.get("urlToImage") else ""
                src = a.get("source", {}).get("name", "") or selected_cat
                st.markdown(f"""
                <a href='{a.get("url","#")}' target='_blank' style='text-decoration:none;'>
                <div class='nc-card'>{img_html}
                    <div class='nc-card-body'>
                        <span class='nc-card-tag'>{src}</span>
                        <p class='nc-card-title'>{a.get("title","")}</p>
                        <p class='nc-card-meta'>{format_date(a.get("publishedAt",""))}</p>
                    </div>
                </div></a>
                """, unsafe_allow_html=True)

    # List
    if len(all_articles) > 7:
        st.markdown(f"<div class='nc-section'>More Stories</div>", unsafe_allow_html=True)
        for a in all_articles[7:]:
            src = a.get("source", {}).get("name", "")
            st.markdown(f"""
            <a href='{a.get("url","#")}' target='_blank' style='text-decoration:none;'>
            <div class='nc-list-item'>
                <p class='nc-list-title'>{a.get("title","")}</p>
                <p class='nc-list-meta'>{src} · {format_date(a.get("publishedAt",""))}</p>
            </div></a>
            """, unsafe_allow_html=True)
