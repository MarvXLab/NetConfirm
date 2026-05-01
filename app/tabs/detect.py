import streamlit as st
from ml.predict import predict
from ml.metadata_encoder import validate_metadata_inputs
from app.components.gauge import render_gauge, render_probability_bars
from db.queries import insert_detection


def render():
    st.markdown("### Analyse an Article")
    st.markdown(
        "<p style='color:#71717a;font-size:14px;margin-top:-12px'>"
        "Paste the article text and provide source metadata for the most accurate result."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── Article Input ──────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    article_text = st.text_area(
        "Article Text",
        placeholder="Paste the full article or a substantial excerpt here...",
        height=200,
        max_chars=10000,
        help="Minimum 20 characters. Longer text produces more accurate results.",
    )

    char_count = len(article_text)
    if char_count > 0:
        color = "#16a34a" if char_count >= 200 else "#f97316"
        st.markdown(
            f"<p style='font-size:12px;color:{color};margin-top:-8px'>"
            f"{char_count:,} characters {'✓' if char_count >= 200 else '— more text improves accuracy'}"
            f"</p>",
            unsafe_allow_html=True,
        )

    # ── Metadata Inputs ────────────────────────────────────
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:13px;font-weight:600;color:#18181b;margin-bottom:4px'>"
        "Source Metadata"
        "</p>"
        "<p style='font-size:12px;color:#71717a;margin-top:-4px'>"
        "These signals capture the social context of the article — not just what it says, but where it came from."
        "</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        trust_score = st.slider(
            "Source Trust Score",
            min_value=0.0, max_value=1.0, value=0.5, step=0.01,
            help="Domain credibility rating (0 = untrusted, 1 = highly trusted). Check mediabiasfactcheck.com",
        )

    with col2:
        follower_count = st.number_input(
            "Author Follower Count",
            min_value=0, max_value=500_000_000, value=1000, step=100,
            help="Number of followers the author/account has on the publishing platform",
        )

    with col3:
        account_age = st.number_input(
            "Account Age (days)",
            min_value=0, max_value=36500, value=365, step=1,
            help="How many days old is the publishing account? Newer accounts are higher risk.",
        )

    source_url = st.text_input(
        "Source URL (optional)",
        placeholder="https://example.com/article",
        help="URL of the article for reference in history",
    )

    # ── Analyse Button ─────────────────────────────────────
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    analyse_clicked = st.button("Analyse Article", type="primary", use_container_width=True)

    if analyse_clicked:
        # Validate
        if len(article_text.strip()) < 20:
            st.error("Please enter at least 20 characters of article text.")
            return

        is_valid, errors = validate_metadata_inputs(trust_score, follower_count, account_age)
        if not is_valid:
            for e in errors:
                st.error(e)
            return

        # Run inference
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

        # ── Results ────────────────────────────────────────
        st.markdown("---")
        st.markdown("### Result")

        verdict_color = "#dc2626" if result["prediction"] == "FAKE" else "#16a34a"
        verdict_bg = "#fef2f2" if result["prediction"] == "FAKE" else "#f0fdf4"
        verdict_icon = "⚠" if result["prediction"] == "FAKE" else "✓"

        st.markdown(
            f"""
            <div style='
                background:{verdict_bg};
                border:1px solid {verdict_color}22;
                border-left:4px solid {verdict_color};
                border-radius:8px;
                padding:16px 20px;
                margin-bottom:16px;
            '>
                <span style='font-size:22px;font-weight:700;color:{verdict_color}'>
                    {verdict_icon} {result["prediction"]}
                </span>
                <span style='font-size:14px;color:#71717a;margin-left:12px'>
                    {round(result["confidence"] * 100, 1)}% confidence
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_gauge, col_meta = st.columns([1.2, 1])

        with col_gauge:
            st.plotly_chart(
                render_gauge(result["fake_prob"], result["prediction"]),
                use_container_width=True,
            )
            st.plotly_chart(
                render_probability_bars(result["fake_prob"], result["real_prob"]),
                use_container_width=True,
            )

        with col_meta:
            st.markdown(
                "<p style='font-size:13px;font-weight:600;color:#18181b;margin-bottom:12px'>"
                "Signal Breakdown"
                "</p>",
                unsafe_allow_html=True,
            )

            def signal_row(label, value, fmt=".3f"):
                bar_width = int(float(value) * 100)
                st.markdown(
                    f"""
                    <div style='margin-bottom:10px'>
                        <div style='display:flex;justify-content:space-between;margin-bottom:3px'>
                            <span style='font-size:12px;color:#52525b'>{label}</span>
                            <span style='font-size:12px;font-weight:600;color:#18181b'>{float(value):{fmt}}</span>
                        </div>
                        <div style='background:#f4f4f5;border-radius:4px;height:6px'>
                            <div style='background:#1a1a2e;border-radius:4px;height:6px;width:{bar_width}%'></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            signal_row("Source Trust Score", trust_score)
            signal_row("Sentiment Polarity", result["sentiment"])
            signal_row("Readability Score", result["readability"])
            signal_row("Fake Probability", result["fake_prob"])
            signal_row("Real Probability", result["real_prob"])

        # Save to DB
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
            pass  # Don't fail the UI if DB write fails

        # Disclaimer
        st.markdown(
            "<p style='font-size:11px;color:#a1a1aa;margin-top:16px'>"
            "NetConfirm provides probabilistic analysis, not definitive fact-checking. "
            "Always verify with primary sources and credible fact-checkers."
            "</p>",
            unsafe_allow_html=True,
        )
