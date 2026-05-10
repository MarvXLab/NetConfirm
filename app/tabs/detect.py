import streamlit as st
import plotly.graph_objects as go
from ml.predict import predict
from ml.metadata_encoder import validate_metadata_inputs
from db.queries import insert_detection


def render_speedometer(real_prob: float, prediction: str) -> go.Figure:
    score = round(real_prob * 100, 1)
    if score >= 75:
        color = "#16a34a"
        label = "Likely Authentic"
    elif score >= 50:
        color = "#eab308"
        label = "Uncertain"
    elif score >= 25:
        color = "#f97316"
        label = "Likely Fake"
    else:
        color = "#dc2626"
        label = "High Risk"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 52, "color": "#18181b", "family": "Inter, sans-serif"}},
        title={"text": f"Authenticity Score<br><span style='font-size:15px;color:#71717a'>{label}</span>",
               "font": {"size": 17, "color": "#18181b", "family": "Inter, sans-serif"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#e4e4e7",
                     "tickfont": {"size": 11, "color": "#71717a"}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "white",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 25],   "color": "#fef2f2"},
                {"range": [25, 50],  "color": "#fff7ed"},
                {"range": [50, 75],  "color": "#fefce8"},
                {"range": [75, 100], "color": "#f0fdf4"},
            ],
            "threshold": {"line": {"color": color, "width": 4}, "thickness": 0.8, "value": score},
        },
    ))
    fig.update_layout(
        height=320, margin={"t": 80, "b": 10, "l": 40, "r": 40},
        paper_bgcolor="white", font={"family": "Inter, sans-serif"},
    )
    return fig


def render():
    dark = st.session_state.get("dark_mode", False)
    bg = "#0f172a" if dark else "#f8fafc"
    card = "#1e293b" if dark else "#ffffff"
    text = "#f1f5f9" if dark else "#18181b"
    sub = "#94a3b8" if dark else "#71717a"
    border = "#334155" if dark else "#e4e4e7"

    # ── State management ──────────────────────────────────
    if "detect_result" not in st.session_state:
        st.session_state["detect_result"] = None
    if "detect_inputs" not in st.session_state:
        st.session_state["detect_inputs"] = None

    # ── RESULT PAGE ───────────────────────────────────────
    if st.session_state["detect_result"] is not None:
        result = st.session_state["detect_result"]
        inputs = st.session_state["detect_inputs"]

        verdict = result["prediction"]
        confidence = round(result["confidence"] * 100, 1)
        verdict_color = "#dc2626" if verdict == "FAKE" else "#16a34a"
        verdict_bg = "#fef2f2" if verdict == "FAKE" else "#f0fdf4"
        verdict_icon = "⚠️" if verdict == "FAKE" else "✅"

        # Back button
        if st.button("← Analyse Another Article", type="secondary"):
            st.session_state["detect_result"] = None
            st.session_state["detect_inputs"] = None
            st.rerun()

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # Verdict banner
        st.markdown(f"""
        <div style='background:{verdict_bg};border:2px solid {verdict_color}33;
                    border-left:6px solid {verdict_color};border-radius:12px;
                    padding:20px 24px;margin-bottom:24px;'>
            <div style='font-size:28px;font-weight:800;color:{verdict_color};margin-bottom:4px;'>
                {verdict_icon} {verdict}
            </div>
            <div style='font-size:15px;color:{verdict_color}cc;'>
                {confidence}% confidence · {'This article shows strong indicators of misinformation.' if verdict == 'FAKE' else 'This article appears to be authentic.'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Speedometer
        st.plotly_chart(render_speedometer(result["real_prob"], verdict), use_container_width=True)

        # Signal breakdown
        st.markdown(f"<p style='font-size:14px;font-weight:700;color:{text};margin:20px 0 12px 0;'>Signal Breakdown</p>", unsafe_allow_html=True)

        signals = [
            ("Source Trust Score", inputs["trust_score"]),
            ("Sentiment Polarity", result["sentiment"]),
            ("Readability Score", result["readability"]),
            ("Fake Probability", result["fake_prob"]),
            ("Real Probability", result["real_prob"]),
        ]
        for label, value in signals:
            bar_w = int(float(value) * 100)
            bar_color = "#16a34a" if label == "Real Probability" else "#dc2626" if label == "Fake Probability" else "#1a1a2e"
            st.markdown(f"""
            <div style='margin-bottom:12px;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                    <span style='font-size:13px;color:{sub};'>{label}</span>
                    <span style='font-size:13px;font-weight:700;color:{text};'>{float(value):.3f}</span>
                </div>
                <div style='background:{"#334155" if dark else "#f4f4f5"};border-radius:6px;height:8px;'>
                    <div style='background:{bar_color};border-radius:6px;height:8px;width:{bar_w}%;transition:width 0.5s;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Article snippet
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:10px;padding:16px;margin-top:20px;'>
            <p style='font-size:12px;font-weight:600;color:{sub};margin:0 0 8px 0;text-transform:uppercase;letter-spacing:0.5px;'>Article Analysed</p>
            <p style='font-size:13px;color:{text};margin:0;line-height:1.6;'>{inputs["article_text"][:400]}{'...' if len(inputs["article_text"]) > 400 else ''}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<p style='font-size:11px;color:{sub};margin-top:16px;'>NetConfirm provides probabilistic analysis, not definitive fact-checking. Always verify with primary sources.</p>", unsafe_allow_html=True)
        return

    # ── INPUT PAGE ────────────────────────────────────────
    st.markdown(f"<h3 style='color:{text};margin-bottom:4px;'>Analyse an Article</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{sub};font-size:14px;margin-top:0;margin-bottom:20px;'>Paste article text and provide source details for the most accurate result.</p>", unsafe_allow_html=True)

    article_text = st.text_area(
        "Article Text",
        placeholder="Paste the full article or a substantial excerpt here...",
        height=200, max_chars=10000,
        help="Minimum 20 characters. Longer text produces more accurate results.",
    )

    char_count = len(article_text)
    if char_count > 0:
        color = "#16a34a" if char_count >= 200 else "#f97316"
        st.markdown(f"<p style='font-size:12px;color:{color};margin-top:-8px;'>{char_count:,} characters {'✓' if char_count >= 200 else '— more text improves accuracy'}</p>", unsafe_allow_html=True)

    st.markdown(f"<p style='font-size:13px;font-weight:600;color:{text};margin:16px 0 4px 0;'>Source Details</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:12px;color:{sub};margin-top:0;'>These signals help assess the credibility of the source.</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        trust_score = st.slider("Source Trust Score", 0.0, 1.0, 0.5, 0.01,
                                help="Domain credibility (0 = untrusted, 1 = highly trusted)")
    with col2:
        follower_count = st.number_input("Author Followers", 0, 500_000_000, 1000, 100,
                                         help="Number of followers the author has")
    with col3:
        account_age = st.number_input("Account Age (days)", 0, 36500, 365, 1,
                                      help="How old is the publishing account?")

    source_url = st.text_input("Source URL (optional)", placeholder="https://example.com/article")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    analyse_clicked = st.button("Analyse Article", type="primary", use_container_width=True)

    if analyse_clicked:
        if len(article_text.strip()) < 20:
            st.error("Please enter at least 20 characters of article text.")
            return

        is_valid, errors = validate_metadata_inputs(trust_score, follower_count, account_age)
        if not is_valid:
            for e in errors:
                st.error(e)
            return

        with st.spinner("Analysing article..."):
            try:
                result = predict(
                    text=article_text,
                    trust_score=trust_score,
                    follower_count=int(follower_count),
                    account_age=int(account_age),
                )
            except RuntimeError as e:
                st.error(str(e))
                return
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                return

        st.session_state["detect_result"] = result
        st.session_state["detect_inputs"] = {
            "article_text": article_text,
            "trust_score": trust_score,
            "follower_count": int(follower_count),
            "account_age": int(account_age),
            "source_url": source_url,
        }

        try:
            insert_detection(
                article_snippet=article_text,
                source_url=source_url or None,
                trust_score=trust_score,
                follower_count=int(follower_count),
                account_age=int(account_age),
                sentiment=result["sentiment"],
                readability=result["readability"],
                prediction=result["prediction"],
                confidence=result["confidence"],
            )
        except Exception:
            pass

        st.rerun()
