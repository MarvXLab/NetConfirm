import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from db.queries import (
    get_stats, get_daily_trend, get_top_fake_snippets,
    get_top_flagged_domains, get_hourly_heatmap, get_confidence_distribution,
)

card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
muted  = "#162032"
red    = "#dc2626"
green  = "#16a34a"
blue   = "#3b82f6"
amber  = "#f59e0b"

DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


TREND_ICON    = "https://cdn-icons-png.flaticon.com/128/12513/12513740.png"
REFRESH_ICON  = "https://cdn-icons-png.flaticon.com/128/16716/16716821.png"


def _no_data_card(msg="Not enough data yet — run some analyses first."):
    st.markdown(f"""
    <div style='background:{muted};border:1px solid {border};border-radius:12px;
        padding:40px;text-align:center;'>
        <img src='{TREND_ICON}' style='width:40px;height:40px;object-fit:contain;
            filter:brightness(0) invert(1);opacity:0.4;margin-bottom:10px;display:block;margin-left:auto;margin-right:auto;'>
        <p style='font-size:14px;color:{sub};margin:0;'>{msg}</p>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown(f"""
    <div style='margin-bottom:20px;display:flex;align-items:center;gap:10px;'>
        <img src='{TREND_ICON}' style='width:24px;height:24px;object-fit:contain;filter:brightness(0) invert(1);'>
        <div>
            <h2 style='font-size:20px;font-weight:800;color:{text};margin:0 0 2px 0;'>Trending Misinformation</h2>
            <p style='font-size:13px;color:{sub};margin:0;'>Live analytics from all NetConfirm detections — updated in real time.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_r, _ = st.columns([1, 6])
    with col_r:
        if st.button("⟳ Refresh", type="secondary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ── Top-level stats ───────────────────────────────────
    try:
        stats = get_stats()
    except Exception:
        stats = None

    if stats and stats["total"]:
        total        = int(stats["total"])
        fake_count   = int(stats["fake_count"] or 0)
        real_count   = int(stats["real_count"] or 0)
        avg_conf     = float(stats["avg_confidence"] or 0)
        fake_pct     = round(fake_count / total * 100, 1) if total else 0

        m1, m2, m3, m4, m5 = st.columns(5)
        for col, label, val, color in [
            (m1, "Total Analyses",  total,              text),
            (m2, "Fake Detected",   fake_count,         red),
            (m3, "Real Verified",   real_count,         green),
            (m4, "Fake Rate",       f"{fake_pct}%",     amber),
            (m5, "Avg Confidence",  f"{avg_conf*100:.1f}%", blue),
        ]:
            col.markdown(f"""
            <div style='background:{card};border:1px solid {border};border-radius:10px;
                padding:16px;text-align:center;margin-bottom:16px;'>
                <p style='font-size:11px;color:{sub};margin:0 0 4px 0;
                    text-transform:uppercase;letter-spacing:0.5px;'>{label}</p>
                <p style='font-size:26px;font-weight:800;color:{color};margin:0;'>{val}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        _no_data_card("No detections yet. Run some analyses to see trends.")
        return

    # ── Row 1: Daily trend + Confidence distribution ──────
    col_trend, col_dist = st.columns([3, 2])

    with col_trend:
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:12px;padding:20px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>📅 Daily Detection Trend (14 days)</p>
            <p style='font-size:11px;color:{sub};margin:0 0 12px 0;'>Fake vs Real articles detected per day</p>
        """, unsafe_allow_html=True)
        try:
            trend = get_daily_trend(14)
        except Exception:
            trend = []

        if trend:
            days_  = [str(r["day"]) for r in trend]
            fakes_ = [int(r["fake_count"]) for r in trend]
            reals_ = [int(r["real_count"]) for r in trend]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=days_, y=fakes_, name="Fake", mode="lines+markers",
                line={"color": red, "width": 2},
                marker={"size": 6, "color": red},
                fill="tozeroy", fillcolor=f"{red}20",
            ))
            fig.add_trace(go.Scatter(
                x=days_, y=reals_, name="Real", mode="lines+markers",
                line={"color": green, "width": 2},
                marker={"size": 6, "color": green},
                fill="tozeroy", fillcolor=f"{green}20",
            ))
            fig.update_layout(
                height=240, margin={"t": 10, "b": 10, "l": 0, "r": 0},
                paper_bgcolor=card, plot_bgcolor=card,
                font={"family": "Inter, sans-serif", "color": text},
                legend={"orientation": "h", "y": -0.2, "font": {"size": 11}},
                xaxis={"showgrid": False, "tickfont": {"size": 10}, "tickangle": -30},
                yaxis={"showgrid": True, "gridcolor": border, "tickfont": {"size": 10}},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(f"<p style='font-size:12px;color:{sub};'>No data for the last 14 days.</p>",
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_dist:
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:12px;padding:20px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>🎯 Confidence Distribution</p>
            <p style='font-size:11px;color:{sub};margin:0 0 12px 0;'>How confident the model is across all verdicts</p>
        """, unsafe_allow_html=True)
        try:
            dist = get_confidence_distribution()
        except Exception:
            dist = []

        if dist:
            fake_buckets = {int(r["bucket"]): int(r["cnt"]) for r in dist if r["prediction"] == "FAKE"}
            real_buckets = {int(r["bucket"]): int(r["cnt"]) for r in dist if r["prediction"] == "REAL"}
            buckets      = list(range(1, 11))
            labels       = [f"{(b-1)*10}–{b*10}%" for b in buckets]

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=labels, y=[fake_buckets.get(b, 0) for b in buckets],
                name="Fake", marker_color=red, opacity=0.85,
            ))
            fig2.add_trace(go.Bar(
                x=labels, y=[real_buckets.get(b, 0) for b in buckets],
                name="Real", marker_color=green, opacity=0.85,
            ))
            fig2.update_layout(
                height=240, barmode="stack",
                margin={"t": 10, "b": 10, "l": 0, "r": 0},
                paper_bgcolor=card, plot_bgcolor=card,
                font={"family": "Inter, sans-serif", "color": text},
                legend={"orientation": "h", "y": -0.25, "font": {"size": 11}},
                xaxis={"showgrid": False, "tickfont": {"size": 9}, "tickangle": -30},
                yaxis={"showgrid": True, "gridcolor": border, "tickfont": {"size": 10}},
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown(f"<p style='font-size:12px;color:{sub};'>No distribution data yet.</p>",
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Row 2: Heatmap + Top domains ──────────────────────
    col_heat, col_domains = st.columns([3, 2])

    with col_heat:
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:12px;padding:20px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>🕐 Activity Heatmap (30 days)</p>
            <p style='font-size:11px;color:{sub};margin:0 0 12px 0;'>When are fake news articles being submitted?</p>
        """, unsafe_allow_html=True)
        try:
            heatmap_data = get_hourly_heatmap()
        except Exception:
            heatmap_data = []

        if heatmap_data:
            # Build 7×24 matrix (dow × hour)
            matrix = np.zeros((7, 24), dtype=int)
            for r in heatmap_data:
                dow  = int(r["dow"])
                hour = int(r["hour"])
                matrix[dow][hour] = int(r["total"])

            fig3 = go.Figure(go.Heatmap(
                z=matrix,
                x=[f"{h:02d}:00" for h in range(24)],
                y=DAYS,
                colorscale=[[0, "#162032"], [0.5, "#7c3aed"], [1, "#dc2626"]],
                showscale=True,
                colorbar={"tickfont": {"size": 9, "color": sub}, "thickness": 10},
            ))
            fig3.update_layout(
                height=220, margin={"t": 10, "b": 10, "l": 0, "r": 0},
                paper_bgcolor=card, plot_bgcolor=card,
                font={"family": "Inter, sans-serif", "color": text},
                xaxis={"tickfont": {"size": 9}, "tickangle": -45, "nticks": 12},
                yaxis={"tickfont": {"size": 10}},
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.markdown(f"<p style='font-size:12px;color:{sub};'>No heatmap data yet.</p>",
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_domains:
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:12px;padding:20px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>🚩 Top Flagged Domains</p>
            <p style='font-size:11px;color:{sub};margin:0 0 16px 0;'>Domains with the most fake detections</p>
        """, unsafe_allow_html=True)
        try:
            domains = get_top_flagged_domains(8)
        except Exception:
            domains = []

        if domains:
            max_count = max(int(d["fake_count"]) for d in domains) or 1
            for d in domains:
                count   = int(d["fake_count"])
                avg_c   = float(d["avg_confidence"])
                bar_pct = int(count / max_count * 100)
                domain  = str(d["domain"] or "unknown")[:35]
                st.markdown(f"""
                <div style='margin-bottom:12px;'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                        <span style='font-size:12px;color:{text};font-weight:500;'>{domain}</span>
                        <span style='font-size:11px;color:{red};font-weight:700;'>{count} fake</span>
                    </div>
                    <div style='background:#0f172a;border-radius:4px;height:5px;'>
                        <div style='background:{red};border-radius:4px;height:5px;width:{bar_pct}%;'></div>
                    </div>
                    <p style='font-size:10px;color:{sub};margin:2px 0 0 0;'>avg confidence {avg_c*100:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <p style='font-size:12px;color:{sub};'>No flagged domains yet.<br>
            Submit articles with source URLs to populate this.</p>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Row 3: Top fake snippets this week ────────────────
    st.markdown(f"""
    <div style='background:{card};border:1px solid {border};border-radius:12px;padding:20px;'>
        <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
            text-transform:uppercase;letter-spacing:0.5px;'>🔥 Top Fake Articles This Week</p>
        <p style='font-size:11px;color:{sub};margin:0 0 16px 0;'>
            Highest-confidence fake detections from the last 7 days
        </p>
    """, unsafe_allow_html=True)

    try:
        snippets = get_top_fake_snippets(8)
    except Exception:
        snippets = []

    if snippets:
        for i, s in enumerate(snippets):
            conf     = float(s["confidence"])
            snippet  = str(s["article_snippet"] or "")[:160]
            src      = str(s["source_url"] or "")
            ts       = s["created_at"]
            try:
                ts_str = ts.strftime("%b %d, %H:%M") if hasattr(ts, "strftime") else str(ts)[:16]
            except Exception:
                ts_str = ""

            conf_color = red if conf >= 0.75 else amber
            src_html   = f"<a href='{src}' target='_blank' style='font-size:10px;color:{blue};'>{src[:60]}{'...' if len(src)>60 else ''}</a>" if src else ""

            st.markdown(f"""
            <div style='display:flex;gap:14px;align-items:flex-start;
                padding:14px 0;border-bottom:1px solid {border};'>
                <div style='font-size:18px;font-weight:800;color:{border};min-width:24px;'>
                    {i+1:02d}
                </div>
                <div style='flex:1;'>
                    <p style='font-size:13px;color:{text};margin:0 0 4px 0;line-height:1.5;'>{snippet}…</p>
                    {src_html}
                    <p style='font-size:10px;color:{sub};margin:4px 0 0 0;'>{ts_str}</p>
                </div>
                <div style='text-align:right;flex-shrink:0;'>
                    <span style='font-size:13px;font-weight:800;color:{conf_color};'>{conf*100:.1f}%</span>
                    <p style='font-size:10px;color:{sub};margin:2px 0 0 0;'>confidence</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='font-size:12px;color:{sub};'>No fake articles detected this week yet.</p>",
                    unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Footer timestamp
    st.markdown(f"""
    <p style='font-size:11px;color:{sub};margin-top:16px;text-align:right;'>
        Last updated: {datetime.now().strftime("%b %d, %Y %H:%M")}
    </p>
    """, unsafe_allow_html=True)
