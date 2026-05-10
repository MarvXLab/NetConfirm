import streamlit as st
import requests
from datetime import datetime

CATEGORIES = ["General", "Technology", "Politics", "Business", "Entertainment", "Sports", "Science", "Health"]

def fetch_news(category="general", page_size=12):
    """Fetch news from NewsAPI — free tier."""
    try:
        api_key = st.secrets.get("newsapi", {}).get("key", "") or ""
        if not api_key:
            import os
            api_key = os.getenv("NEWSAPI_KEY", "")
        if not api_key:
            return None, "No NewsAPI key configured."

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "category": category.lower(),
            "language": "en",
            "pageSize": page_size,
            "apiKey": api_key,
        }
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        if data.get("status") == "ok":
            return data.get("articles", []), None
        return None, data.get("message", "Failed to fetch news.")
    except Exception as e:
        return None, str(e)


def format_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except Exception:
        return date_str or ""


def render():
    dark = st.session_state.get("dark_mode", False)
    bg = "#0f1f1a" if dark else "#f0f7f4"
    card_bg = "#1a2e28" if dark else "#ffffff"
    text = "#e8f5f0" if dark else "#0d1f1a"
    sub = "#8ab5a8" if dark else "#4a7a6a"
    tag_bg = "#dc2626"
    accent = "#16a34a"

    st.markdown(f"""
    <style>
    .news-wrap {{ background: {bg}; padding: 0; }}
    .news-header {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 16px 0 12px 0; border-bottom: 1px solid {'#2a3f38' if dark else '#d1e8df'};
        margin-bottom: 16px;
    }}
    .news-logo {{ font-size: 28px; font-weight: 900; color: {text}; letter-spacing: -1px; }}
    .news-logo span {{ color: {accent}; }}
    .news-date {{ font-size: 12px; color: {sub}; }}
    .ticker-wrap {{
        background: {'#1a2e28' if dark else '#e8f5f0'};
        border-radius: 8px; padding: 10px 16px;
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 20px; overflow: hidden;
    }}
    .ticker-label {{
        background: {tag_bg}; color: white; font-size: 11px; font-weight: 700;
        padding: 3px 10px; border-radius: 4px; white-space: nowrap; flex-shrink: 0;
    }}
    .ticker-text {{ font-size: 13px; color: {text}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
    .hero-card {{
        background: {card_bg}; border-radius: 16px; overflow: hidden;
        margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,{'0.3' if dark else '0.08'});
    }}
    .hero-img {{ width: 100%; height: 280px; object-fit: cover; }}
    .hero-body {{ padding: 20px; }}
    .hero-meta {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
    .hero-date {{ font-size: 12px; color: {sub}; }}
    .hero-tag {{ background: {tag_bg}; color: white; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 20px; }}
    .hero-title {{ font-size: 22px; font-weight: 800; color: {text}; line-height: 1.3; margin: 0; }}
    .hero-desc {{ font-size: 13px; color: {sub}; margin-top: 8px; line-height: 1.5; }}
    .section-header {{
        display: flex; align-items: center; justify-content: space-between;
        margin: 24px 0 16px 0;
    }}
    .section-title {{ font-size: 20px; font-weight: 800; color: {text}; }}
    .news-card {{
        background: {card_bg}; border-radius: 12px; overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,{'0.25' if dark else '0.06'});
        height: 100%; transition: transform 0.2s;
    }}
    .news-card:hover {{ transform: translateY(-2px); }}
    .news-card-img {{ width: 100%; height: 140px; object-fit: cover; }}
    .news-card-body {{ padding: 14px; }}
    .news-card-tag {{ display: inline-block; background: {tag_bg}; color: white; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 20px; margin-bottom: 8px; }}
    .news-card-title {{ font-size: 14px; font-weight: 700; color: {text}; line-height: 1.4; margin: 0; }}
    .news-card-source {{ font-size: 11px; color: {sub}; margin-top: 6px; }}
    .cat-btn {{
        display: inline-block; padding: 6px 14px; border-radius: 20px; font-size: 12px;
        font-weight: 600; cursor: pointer; margin: 0 4px 8px 0;
        background: {'#2a3f38' if dark else '#e8f5f0'}; color: {text};
        border: 1px solid {'#3a5f50' if dark else '#c1ddd4'};
    }}
    .cat-btn.active {{ background: {accent}; color: white; border-color: {accent}; }}
    </style>
    """, unsafe_allow_html=True)

    # Header
    today = datetime.now().strftime("%A, %B %d, %Y")
    st.markdown(f"""
    <div class='news-header'>
        <div>
            <div class='news-logo'>net<span>confirm</span></div>
            <div class='news-date'>{today}</div>
        </div>
        <div style='font-size:12px;color:{sub};font-weight:600;'>Verified News Feed</div>
    </div>
    """, unsafe_allow_html=True)

    # Category selector
    selected_cat = st.session_state.get("news_category", "General")
    cols = st.columns(len(CATEGORIES))
    for i, cat in enumerate(CATEGORIES):
        with cols[i]:
            if st.button(cat, key=f"cat_{cat}", use_container_width=True,
                        type="primary" if cat == selected_cat else "secondary"):
                st.session_state["news_category"] = cat
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Fetch news
    with st.spinner("Loading latest news..."):
        articles, error = fetch_news(selected_cat)

    if error:
        st.error(f"Could not load news: {error}")
        st.info("To enable the news feed, add your NewsAPI key. Get a free key at newsapi.org")
        return

    if not articles:
        st.info("No articles found for this category.")
        return

    # Filter out articles without images
    with_img = [a for a in articles if a.get("urlToImage")]
    without_img = [a for a in articles if not a.get("urlToImage")]
    all_articles = with_img + without_img

    # Ticker — latest headlines
    headlines = " · ".join([a["title"] for a in all_articles[:5] if a.get("title")])
    st.markdown(f"""
    <div class='ticker-wrap'>
        <span class='ticker-label'>Latest</span>
        <span class='ticker-text'>{headlines}</span>
    </div>
    """, unsafe_allow_html=True)

    # Hero article
    if all_articles:
        hero = all_articles[0]
        hero_img = hero.get("urlToImage", "")
        hero_title = hero.get("title", "")
        hero_desc = hero.get("description", "")
        hero_date = format_date(hero.get("publishedAt", ""))
        hero_source = hero.get("source", {}).get("name", "")
        hero_url = hero.get("url", "#")

        img_html = f"<img src='{hero_img}' class='hero-img' onerror=\"this.style.display='none'\">" if hero_img else ""
        st.markdown(f"""
        <a href='{hero_url}' target='_blank' style='text-decoration:none;'>
        <div class='hero-card'>
            {img_html}
            <div class='hero-body'>
                <div class='hero-meta'>
                    <span class='hero-date'>📅 {hero_date}</span>
                    <span class='hero-tag'>{hero_source or selected_cat}</span>
                </div>
                <p class='hero-title'>{hero_title}</p>
                <p class='hero-desc'>{hero_desc or ''}</p>
            </div>
        </div>
        </a>
        """, unsafe_allow_html=True)

    # Highlight grid
    st.markdown(f"""
    <div class='section-header'>
        <span class='section-title'>Highlight News</span>
    </div>
    """, unsafe_allow_html=True)

    grid_articles = all_articles[1:7]
    if grid_articles:
        cols = st.columns(3)
        for i, article in enumerate(grid_articles):
            with cols[i % 3]:
                img = article.get("urlToImage", "")
                title = article.get("title", "")
                source = article.get("source", {}).get("name", "")
                url = article.get("url", "#")
                date = format_date(article.get("publishedAt", ""))
                img_html = f"<img src='{img}' class='news-card-img' onerror=\"this.style.display='none'\">" if img else ""
                st.markdown(f"""
                <a href='{url}' target='_blank' style='text-decoration:none;'>
                <div class='news-card'>
                    {img_html}
                    <div class='news-card-body'>
                        <span class='news-card-tag'>{source or selected_cat}</span>
                        <p class='news-card-title'>{title}</p>
                        <p class='news-card-source'>📅 {date}</p>
                    </div>
                </div>
                </a>
                """, unsafe_allow_html=True)
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # More articles list
    if len(all_articles) > 7:
        st.markdown(f"<div class='section-title' style='margin:20px 0 12px 0;'>More Stories</div>", unsafe_allow_html=True)
        for article in all_articles[7:]:
            title = article.get("title", "")
            source = article.get("source", {}).get("name", "")
            url = article.get("url", "#")
            date = format_date(article.get("publishedAt", ""))
            st.markdown(f"""
            <a href='{url}' target='_blank' style='text-decoration:none;'>
            <div style='background:{card_bg};border-radius:10px;padding:14px 16px;margin-bottom:8px;
                        border-left:3px solid {accent};'>
                <p style='font-size:14px;font-weight:600;color:{text};margin:0 0 4px 0;'>{title}</p>
                <p style='font-size:11px;color:{sub};margin:0;'>{source} · {date}</p>
            </div>
            </a>
            """, unsafe_allow_html=True)
