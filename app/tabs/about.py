import streamlit as st


def render():
    st.markdown("### About NetConfirm")
    st.markdown(
        "<p style='color:#71717a;font-size:14px;margin-top:-12px'>"
        "A hybrid fake news detection system combining deep language understanding with social context analysis."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # How it works
    st.markdown("#### How It Works")
    st.markdown(
        """
        NetConfirm uses a two-stream hybrid architecture:

        **Text Stream — DistilBERT**
        The article text is encoded using DistilBERT, a transformer model that understands
        deep semantic meaning, writing style, and linguistic patterns. It produces a
        768-dimensional representation of the article's content.

        **Metadata Stream — Social Context**
        Five structured signals capture how and where the article was published:
        - **Source Trust Score** — credibility rating of the publishing domain
        - **Author Follower Count** — reach and influence of the author
        - **Account Age** — newly created accounts are higher risk
        - **Sentiment Polarity** — emotional manipulation is a common fake news signal
        - **Readability Score** — fake news often targets lower reading levels

        **Fusion + Classification**
        Both streams are concatenated into a 773-dimensional hybrid vector and
        classified by an XGBoost ensemble model trained on 72,000+ labeled articles
        from the WELFake benchmark dataset.
        """,
        unsafe_allow_html=False,
    )

    st.markdown("---")

    # Performance
    st.markdown("#### Model Performance")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Accuracy", "96.4%")
    col2.metric("F1 Score", "0.963")
    col3.metric("Training Set", "57,600")
    col4.metric("Test Set", "14,400")

    st.markdown("---")

    # Interpretation guide
    st.markdown("#### Interpreting Results")
    st.markdown(
        """
        | Authenticity Score | Interpretation |
        |---|---|
        | 75% – 100% | Likely authentic — low misinformation risk |
        | 50% – 74% | Uncertain — verify with additional sources |
        | 25% – 49% | Likely fake — treat with significant caution |
        | 0% – 24% | High risk — strong indicators of misinformation |
        """
    )

    st.markdown("---")

    # Disclaimer
    st.markdown("#### Important Disclaimer")
    st.markdown(
        "<p style='font-size:13px;color:#71717a'>"
        "NetConfirm is a probabilistic analysis tool, not a definitive fact-checker. "
        "Results should be treated as one signal among many. Always verify important "
        "claims with primary sources, credible journalists, and established fact-checking "
        "organisations such as Africa Check, Snopes, or PolitiFact. "
        "The system may exhibit reduced accuracy on highly contemporary events or "
        "content that differs substantially from its training distribution."
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<p style='font-size:12px;color:#a1a1aa'>"
        "Built by Taiwo Emmanuel · Westland University · Computer Science FYP · 2025"
        "</p>",
        unsafe_allow_html=True,
    )
