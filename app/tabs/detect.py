import streamlit as st
import plotly.graph_objects as go
from ml.predict import predict
from ml.metadata_encoder import validate_metadata_inputs
from db.queries import insert_detection

F = "invert(14%) sepia(20%) saturate(800%) hue-rotate(190deg) brightness(80%) contrast(95%)"

def render_speedometer(real_prob: float) -> go.Figure:
    score = round(real_prob * 100, 1)
    if score >= 75:
        color, label = "#16a34a", "Likely Authentic"
    elif score >= 50:
        color, label = "#eab308", "Uncertain"
    elif score >= 25:
        color, label = "#f97316", "Likely Fake"
    else:
        color, label = "#dc2626", "High Risk"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 48, "color": "#0f172a", "family": "Inter, sans-serif"}},
        title={"text": f"Authenticity Score<br><span style='font-size:14px;color:#64748b;font-weight:500'>{label}</span>",
               "font": {"size": 16, "color": "#0f172a", "family": "Inter, sans-serif"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#e2e8f0",
                     "tickfont": {"size": 11, "color": "#94a3b8"}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "white", "borderwidth": 0,
            "steps": [
                {"range": [0, 25],   "color": "#fef2f2"},
                {"range": [25, 50],  "color": "#fff7ed"},
                {"range": [50, 75],  "color": "#fefce8"},
                {"range": [75, 100], "color": "#f0fdf4"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": score},
        },
    ))
    fig.update_layout(height=300, margin={"t": 80, "b": 0, "l": 30, "r": 30},
                      paper_bgcolor="white", font={"family": "Inter, sans-serif"})
    return fig


def render():
    dark   = st.session_state.get("dark_mode", False)
    card   = "#1e293b" if dark else "#ffffff"
    text   = "#f1f5f9" if dark else "#0f172a"
    sub    = "#94a3b8" if dark else "#64748b"
    border = "#334155" if dark else "#e2e8f0"
    muted  = "#1e293b" if dark else "#f8fafc"

    if "detect_result" not in st.session_state:
        st.session_state["detect_result"] = None
    if "detect_inputs" not in st.session_state:
        st.session_state["detect_inputs"] = None

    # ── RESULT VIEW ───────────────────────────────────────
    if st.session_state["detect_result"] is not None:
        result = st.session_state["detect_result"]
        inputs = st.session_state["detect_inputs"]
        verdict    = result["prediction"]
        confidence = round(result["confidence"] * 100, 1)
        is_fake    = verdict == "FAKE"
        v_color    = "#dc2626" if is_fake else "#16a34a"
        v_bg       = "#fef2f2" if is_fake else "#f0fdf4"
        v_icon     = "⚠️" if is_fake else "✅"
        v_msg      = "Strong indicators of misinformation detected." if is_fake else "This article appears authentic and credible."

        col_back, _ = st.columns([2, 5])
        with col_back:
            if st.button("← New Analysis", type="secondary"):
                st.session_state["detect_result"] = None
                st.session_state["detect_inputs"] = None
                st.rerun()

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:{v_bg};border:1px solid {v_color}30;border-left:5px solid {v_color};
            border-radius:12px;padding:20px 24px;margin-bottom:24px;'>
            <div style='display:flex;align-items:center;gap:12px;'>
                <span style='font-size:32px;'>{v_icon}</span>
                <div>
                    <div style='font-size:24px;font-weight:800;color:{v_color};line-height:1;'>{verdict}</div>
                    <div style='font-size:14px;color:{v_color}bb;margin-top:4px;'>{confidence}% confidence · {v_msg}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_gauge, col_signals = st.columns([1, 1])
        with col_gauge:
            st.markdown(f"<div style='background:white;border:1px solid {border};border-radius:12px;padding:16px;'>", unsafe_allow_html=True)
            st.plotly_chart(render_speedometer(result["real_prob"]), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_signals:
            st.markdown(f"""
            <div style='background:{card};border:1px solid {border};border-radius:12px;padding:20px;'>
                <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 16px 0;
                    text-transform:uppercase;letter-spacing:0.5px;'>Signal Breakdown</p>
            """, unsafe_allow_html=True)
            for label, value, color in [
                ("Source Trust",     inputs["trust_score"],  "#3b82f6"),
                ("Sentiment",        result["sentiment"],    "#8b5cf6"),
                ("Readability",      result["readability"],  "#f59e0b"),
                ("Fake Probability", result["fake_prob"],    "#dc2626"),
                ("Real Probability", result["real_prob"],    "#16a34a"),
            ]:
                bar_w = int(float(value) * 100)
                st.markdown(f"""
                <div style='margin-bottom:14px;'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
                        <span style='font-size:12px;color:{sub};font-weight:500;'>{label}</span>
                        <span style='font-size:12px;font-weight:700;color:{text};'>{float(value):.3f}</span>
                    </div>
                    <div style='background:{"#334155" if dark else "#f1f5f9"};border-radius:4px;height:6px;'>
                        <div style='background:{color};border-radius:4px;height:6px;width:{bar_w}%;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:{muted};border:1px solid {border};border-radius:12px;padding:18px 20px;margin-top:20px;'>
            <p style='font-size:11px;font-weight:700;color:{sub};margin:0 0 10px 0;text-transform:uppercase;letter-spacing:0.8px;'>Article Analysed</p>
            <p style='font-size:13px;color:{text};margin:0;line-height:1.7;'>{inputs["article_text"][:500]}{'...' if len(inputs["article_text"]) > 500 else ''}</p>
        </div>
        <p style='font-size:11px;color:{sub};margin-top:14px;line-height:1.6;'>
            ⚠ NetConfirm provides probabilistic analysis, not definitive fact-checking. Always verify with primary sources.
        </p>
        """, unsafe_allow_html=True)
        return

    # ── INPUT VIEW ────────────────────────────────────────
    st.markdown(f"""
    <style>
    @keyframes pulse-ai {{
        0%,100% {{ transform:scale(1); opacity:1; }}
        50% {{ transform:scale(1.2); opacity:0.75; }}
    }}
    .ai-icon {{ animation:pulse-ai 2.5s ease-in-out infinite; display:inline-block; }}
    </style>
    """, unsafe_allow_html=True)

    col_form, col_info = st.columns([3, 1])

    with col_form:
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:14px;
            padding:24px 24px 8px 24px;box-shadow:0 2px 12px rgba(0,0,0,0.05);margin-bottom:16px;'>
            <h3 style='font-size:18px;font-weight:800;color:{text};margin:0 0 4px 0;'>Analyse an Article</h3>
            <p style='font-size:13px;color:{sub};margin:0 0 0 0;'>Paste article text and fill in source details for the most accurate result.</p>
        </div>
        """, unsafe_allow_html=True)

        article_text = st.text_area("Article Text *", placeholder="Paste the full article or a substantial excerpt here...",
                                    height=220, max_chars=10000)
        char_count = len(article_text)
        if char_count > 0:
            ok = char_count >= 200
            st.markdown(f"<p style='font-size:12px;color:{'#16a34a' if ok else '#f97316'};margin-top:-6px;'>"
                        f"{char_count:,} characters {'· Good length ✓' if ok else '· More text improves accuracy'}</p>",
                        unsafe_allow_html=True)

        st.markdown(f"<p style='font-size:13px;font-weight:600;color:{text};margin:18px 0 6px 0;'>Source Details</p>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            trust_score = st.slider("Trust Score", 0.0, 1.0, 0.5, 0.01, help="Domain credibility (0=untrusted, 1=trusted)")
        with c2:
            follower_count = st.number_input("Author Followers", 0, 500_000_000, 1000, 100)
        with c3:
            account_age = st.number_input("Account Age (days)", 0, 36500, 365, 1)

        source_url = st.text_input("Source URL (optional)", placeholder="https://example.com/article")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        clicked = st.button("🔍  Analyse Article", type="primary", use_container_width=True)

    with col_info:
        st.markdown(f"""
        <div style='background:{muted};border:1px solid {border};border-radius:12px;padding:20px;'>
            <p style='font-size:11px;font-weight:700;color:{text};margin:0 0 14px 0;text-transform:uppercase;letter-spacing:0.5px;'>How It Works</p>
            <div style='display:flex;flex-direction:column;gap:14px;'>
                <div style='display:flex;gap:12px;align-items:flex-start;'>
                    <img src='https://cdn-icons-png.flaticon.com/128/748/748035.png'
                        style='width:22px;height:22px;object-fit:contain;flex-shrink:0;margin-top:1px;filter:{F};'>
                    <p style='font-size:12px;color:{sub};margin:0;line-height:1.5;'>Paste any article text — news, social posts, blog content.</p>
                </div>
                <div style='display:flex;gap:12px;align-items:flex-start;'>
                    <img src='https://cdn-icons-png.flaticon.com/128/16398/16398385.png'
                        style='width:22px;height:22px;object-fit:contain;flex-shrink:0;margin-top:1px;filter:{F};'>
                    <p style='font-size:12px;color:{sub};margin:0;line-height:1.5;'>Add source details to improve accuracy with social context signals.</p>
                </div>
                <div style='display:flex;gap:12px;align-items:flex-start;'>
                    <span class='ai-icon'>
                        <img src='https://cdn-icons-png.flaticon.com/128/18337/18337835.png'
                            style='width:22px;height:22px;object-fit:contain;display:block;filter:{F};'>
                    </span>
                    <p style='font-size:12px;color:{sub};margin:0;line-height:1.5;'>DistilBERT encodes the text. XGBoost classifies using 773 features.</p>
                </div>
                <div style='display:flex;gap:12px;align-items:flex-start;'>
                    <img src='https://cdn-icons-png.flaticon.com/128/9912/9912366.png'
                        style='width:22px;height:22px;object-fit:contain;flex-shrink:0;margin-top:1px;filter:{F};'>
                    <p style='font-size:12px;color:{sub};margin:0;line-height:1.5;'>Get a verdict with confidence score and signal breakdown.</p>
                </div>
            </div>
            <div style='margin-top:16px;padding-top:14px;border-top:1px solid {border};'>
                <p style='font-size:11px;font-weight:700;color:{text};margin:0 0 8px 0;'>Model Performance</p>
                <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                    <span style='font-size:11px;color:{sub};'>Accuracy</span>
                    <span style='font-size:11px;font-weight:700;color:#16a34a;'>96.4%</span>
                </div>
                <div style='display:flex;justify-content:space-between;'>
                    <span style='font-size:11px;color:{sub};'>F1 Score</span>
                    <span style='font-size:11px;font-weight:700;color:#16a34a;'>0.963</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if clicked:
        if len(article_text.strip()) < 20:
            st.error("Please enter at least 20 characters.")
            return
        is_valid, errors = validate_metadata_inputs(trust_score, follower_count, account_age)
        if not is_valid:
            for e in errors:
                st.error(e)
            return
        with st.spinner("Analysing article..."):
            try:
                result = predict(text=article_text, trust_score=trust_score,
                                 follower_count=int(follower_count), account_age=int(account_age))
            except RuntimeError as e:
                st.error(str(e)); return
            except Exception as e:
                st.error(f"Analysis failed: {e}"); return

        st.session_state["detect_result"] = result
        st.session_state["detect_inputs"] = {
            "article_text": article_text, "trust_score": trust_score,
            "follower_count": int(follower_count), "account_age": int(account_age),
            "source_url": source_url,
        }
        try:
            insert_detection(article_snippet=article_text, source_url=source_url or None,
                             trust_score=trust_score, follower_count=int(follower_count),
                             account_age=int(account_age), sentiment=result["sentiment"],
                             readability=result["readability"], prediction=result["prediction"],
                             confidence=result["confidence"])
        except Exception:
            pass
        st.rerun()
