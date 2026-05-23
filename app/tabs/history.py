import streamlit as st
import pandas as pd
from db.queries import get_recent_detections, get_stats

HIST_ICON  = "https://cdn-icons-png.flaticon.com/128/6619/6619116.png"
EMPTY_ICON = "https://cdn-icons-png.flaticon.com/128/8423/8423644.png"

card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
muted  = "#162032"


def render():
    st.markdown(f"""
    <div style='margin-bottom:20px;display:flex;align-items:center;gap:10px;'>
        <img src='{HIST_ICON}' style='width:24px;height:24px;object-fit:contain;filter:brightness(0) invert(1);'>
        <div>
            <h2 style='font-size:20px;font-weight:800;color:{text};margin:0 0 2px 0;'>Detection History</h2>
            <p style='font-size:13px;color:{sub};margin:0;'>All previous analyses stored for audit and review.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Row ──────────────────────────────────────────
    try:
        stats = get_stats()
        if stats and stats["total"]:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Analyses", f"{stats['total']:,}")
            col2.metric("Fake Detected", f"{stats['fake_count']:,}")
            col3.metric("Real Verified", f"{stats['real_count']:,}")
            col4.metric("Avg Confidence", f"{float(stats['avg_confidence']) * 100:.1f}%")
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    except Exception:
        pass

    # ── History Table ──────────────────────────────────────
    try:
        rows = get_recent_detections(limit=50)
    except Exception as e:
        st.error(f"Could not load history: {e}")
        return

    if not rows:
        st.markdown(
            f"<div style='text-align:center;padding:48px;'>"
            f"<img src='{EMPTY_ICON}' style='width:56px;height:56px;object-fit:contain;"
            f"filter:brightness(0) invert(1);opacity:0.5;display:block;margin:0 auto 14px auto;'>"
            f"<p style='font-size:15px;color:{text};font-weight:600;margin:0 0 6px 0;'>No detections yet.</p>"
            f"<p style='font-size:13px;color:{sub};margin:0;'>Run your first analysis in the Detect tab.</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
        return

    df = pd.DataFrame(rows)
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
    df["confidence"] = (df["confidence"] * 100).round(1).astype(str) + "%"
    df["trust_score"] = df["trust_score"].round(3)
    df["article_snippet"] = df["article_snippet"].str[:80] + "..."

    df = df.rename(columns={
        "id": "ID",
        "article_snippet": "Article Snippet",
        "prediction": "Verdict",
        "confidence": "Confidence",
        "trust_score": "Trust Score",
        "created_at": "Analysed At",
    })

    df = df[["ID", "Article Snippet", "Verdict", "Confidence", "Trust Score", "Analysed At"]]

    # Color verdict column
    def color_verdict(val):
        if val == "FAKE":
            return "color: #dc2626; font-weight: 600"
        return "color: #16a34a; font-weight: 600"

    styled = df.style.applymap(color_verdict, subset=["Verdict"])

    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.markdown(
        f"<p style='font-size:12px;color:#64748b'>Showing last {len(df)} detections</p>",
        unsafe_allow_html=True,
    )
