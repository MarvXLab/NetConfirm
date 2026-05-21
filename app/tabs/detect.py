import streamlit as st
import plotly.graph_objects as go
from ml.predict import predict
from ml.metadata_encoder import validate_metadata_inputs
from ml.explainer import get_shap_explanation
from ml.translator import detect_language, translate_to_english, get_language_flag
from db.queries import insert_detection
from app.components.verdict_card import generate_verdict_card

F = "brightness(0) invert(1)"


def scrape_url(url: str):
    try:
        from newspaper import Article
        a = Article(url, request_timeout=10)
        a.download()
        a.parse()
        if not a.text or len(a.text.strip()) < 50:
            return None, "Could not extract article text from this URL."
        return {"text": a.text, "title": a.title, "top_image": a.top_image, "source_url": url}, None
    except Exception as e:
        return None, f"Could not scrape URL: {e}"


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
        number={"suffix": "%", "font": {"size": 48, "color": "#f1f5f9", "family": "Inter, sans-serif"}},
        title={"text": f"Authenticity Score<br><span style='font-size:14px;color:#94a3b8;font-weight:500'>{label}</span>",
               "font": {"size": 16, "color": "#f1f5f9", "family": "Inter, sans-serif"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#334155",
                     "tickfont": {"size": 11, "color": "#94a3b8"}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#1e293b", "borderwidth": 0,
            "steps": [
                {"range": [0, 25],   "color": "#2d1515"},
                {"range": [25, 50],  "color": "#2d1f0f"},
                {"range": [50, 75],  "color": "#2d2a0f"},
                {"range": [75, 100], "color": "#0f2d15"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.75, "value": score},
        },
    ))
    fig.update_layout(height=300, margin={"t": 80, "b": 0, "l": 30, "r": 30},
                      paper_bgcolor="#1e293b", font={"family": "Inter, sans-serif"})
    return fig


def render():
    card   = "#1e293b"
    text   = "#f1f5f9"
    sub    = "#94a3b8"
    border = "#334155"
    muted  = "#162032"

    if "detect_result" not in st.session_state:
        st.session_state["detect_result"] = None
    if "detect_inputs" not in st.session_state:
        st.session_state["detect_inputs"] = None

    st.markdown("""
    <style>
    @keyframes pulse-ai {
        0%,100% { transform:scale(1); opacity:1; }
        50% { transform:scale(1.2); opacity:0.75; }
    }
    .ai-icon { animation:pulse-ai 2.5s ease-in-out infinite; display:inline-block; }
    </style>
    """, unsafe_allow_html=True)

    # ── RESULT VIEW ───────────────────────────────────────
    if st.session_state["detect_result"] is not None:
        result = st.session_state["detect_result"]
        inputs = st.session_state["detect_inputs"]
        verdict    = result["prediction"]
        confidence = round(result["confidence"] * 100, 1)
        is_fake    = verdict == "FAKE"
        v_color    = "#dc2626" if is_fake else "#16a34a"
        v_bg = "#2d1515" if is_fake else "#0f2d15"
        v_icon     = "⚠️" if is_fake else "✅"
        v_msg      = "Strong indicators of misinformation detected." if is_fake else "This article appears authentic and credible."

        col_back, _ = st.columns([2, 5])
        with col_back:
            if st.button("← New Analysis", type="secondary"):
                st.session_state["detect_result"] = None
                st.session_state["detect_inputs"] = None
                st.rerun()

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Show scraped article image if available
        if inputs.get("top_image"):
            st.markdown(f"""
            <div style='border-radius:12px;overflow:hidden;margin-bottom:16px;max-height:240px;'>
                <img src='{inputs["top_image"]}' style='width:100%;height:240px;object-fit:cover;display:block;'
                    onerror="this.style.display='none'">
            </div>
            """, unsafe_allow_html=True)

        if inputs.get("title"):
            st.markdown(f"<h2 style='font-size:20px;font-weight:800;color:{text};margin:0 0 16px 0;'>{inputs['title']}</h2>",
                        unsafe_allow_html=True)

        # Language badge
        if inputs.get("lang_code", "en") != "en":
            flag = get_language_flag(inputs["lang_code"])
            st.markdown(f"""
            <div style='display:inline-flex;align-items:center;gap:8px;background:#1e3a5f;
                border:1px solid #3b82f6;border-radius:8px;padding:6px 14px;margin-bottom:16px;'>
                <span style='font-size:16px;'>{flag}</span>
                <span style='font-size:12px;color:#93c5fd;font-weight:600;'>
                    Detected: {inputs['lang_name']} · Auto-translated to English for analysis
                </span>
            </div>
            """, unsafe_allow_html=True)

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

        # ── Share verdict card ──────────────────────────────
        try:
            card_bytes = generate_verdict_card(
                verdict=result["prediction"],
                confidence=result["confidence"],
                real_prob=result["real_prob"],
                fake_prob=result["fake_prob"],
                sentiment=result["sentiment"],
                title=inputs.get("title", ""),
                snippet=inputs["article_text"][:120],
            )
            col_dl, _ = st.columns([2, 5])
            with col_dl:
                st.download_button(
                    label="📤  Download Verdict Card",
                    data=card_bytes,
                    file_name=f"netconfirm_{result['prediction'].lower()}.png",
                    mime="image/png",
                    type="secondary",
                    use_container_width=True,
                )
        except Exception:
            pass

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col_gauge, col_signals = st.columns([1, 1])
        with col_gauge:
            st.markdown(f"<div style='background:{card};border:1px solid {border};border-radius:12px;padding:16px;'>",
                        unsafe_allow_html=True)
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
                    <div style='background:#334155;border-radius:4px;height:6px;'>
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

        # ── SHAP EXPLANATION PANEL ────────────────────────
        st.markdown(f"""
        <div style='margin-top:28px;border-top:1px solid {border};padding-top:24px;'>
            <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px;'>
                <span style='font-size:20px;'>🔬</span>
                <span style='font-size:16px;font-weight:800;color:{text};'>Why did the AI decide this?</span>
            </div>
            <p style='font-size:13px;color:{sub};margin:0 0 20px 0;'>
                SHAP values show exactly which words and signals pushed the verdict — red = towards FAKE, green = towards REAL.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Computing explanation..."):
            try:
                word_scores, feature_scores, base_value = get_shap_explanation(
                    text=inputs["article_text"],
                    trust_score=inputs["trust_score"],
                    follower_count=inputs["follower_count"],
                    account_age=inputs["account_age"],
                )
                shap_ok = True
            except Exception as e:
                shap_ok = False
                st.warning(f"Explanation unavailable: {e}")

        if shap_ok:
            col_words, col_feats = st.columns([1, 1])

            # ── Top words chart ───────────────────────────
            with col_words:
                st.markdown(f"""
                <div style='background:{card};border:1px solid {border};border-radius:12px;padding:20px;'>
                    <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
                        text-transform:uppercase;letter-spacing:0.5px;'>🔤 Top Influential Words</p>
                    <p style='font-size:11px;color:{sub};margin:0 0 16px 0;'>Words with the biggest impact on the verdict</p>
                """, unsafe_allow_html=True)

                if word_scores:
                    top_words = word_scores[:12]
                    fig_words = go.Figure(go.Bar(
                        x=[v for _, v in top_words],
                        y=[w for w, _ in top_words],
                        orientation="h",
                        marker_color=["#dc2626" if v > 0 else "#16a34a" for _, v in top_words],
                        text=[f"{v:+.3f}" for _, v in top_words],
                        textposition="outside",
                        textfont={"size": 10, "color": "#94a3b8"},
                    ))
                    fig_words.update_layout(
                        height=320, margin={"t": 10, "b": 10, "l": 10, "r": 60},
                        paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
                        font={"family": "Inter, sans-serif", "color": "#f1f5f9"},
                        xaxis={"showgrid": False, "zeroline": True,
                               "zerolinecolor": "#334155", "tickfont": {"size": 10}},
                        yaxis={"tickfont": {"size": 11}, "autorange": "reversed"},
                    )
                    st.plotly_chart(fig_words, use_container_width=True)
                else:
                    st.markdown(f"<p style='font-size:12px;color:{sub};'>No significant word signals found.</p>",
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # ── Feature signals chart ─────────────────────
            with col_feats:
                st.markdown(f"""
                <div style='background:{card};border:1px solid {border};border-radius:12px;padding:20px;'>
                    <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
                        text-transform:uppercase;letter-spacing:0.5px;'>📊 Signal Contributions</p>
                    <p style='font-size:11px;color:{sub};margin:0 0 16px 0;'>How each signal pushed the model's decision</p>
                """, unsafe_allow_html=True)

                top_feats = feature_scores[:10]
                fig_feats = go.Figure(go.Bar(
                    x=[v for _, v in top_feats],
                    y=[n for n, _ in top_feats],
                    orientation="h",
                    marker_color=["#dc2626" if v > 0 else "#16a34a" for _, v in top_feats],
                    text=[f"{v:+.3f}" for _, v in top_feats],
                    textposition="outside",
                    textfont={"size": 10, "color": "#94a3b8"},
                ))
                fig_feats.update_layout(
                    height=320, margin={"t": 10, "b": 10, "l": 10, "r": 60},
                    paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
                    font={"family": "Inter, sans-serif", "color": "#f1f5f9"},
                    xaxis={"showgrid": False, "zeroline": True,
                           "zerolinecolor": "#334155", "tickfont": {"size": 10}},
                    yaxis={"tickfont": {"size": 11}, "autorange": "reversed"},
                )
                st.plotly_chart(fig_feats, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # ── Highlighted article text ──────────────────
            fake_words  = {w for w, v in word_scores if v > 0.001}
            real_words  = {w for w, v in word_scores if v < -0.001}
            article_preview = inputs["article_text"][:800]
            highlighted = ""
            for word in article_preview.split():
                clean = word.lower().strip(".,!?\"'();:")
                if clean in fake_words:
                    highlighted += f"<mark style='background:#dc262630;color:#fca5a5;border-radius:3px;padding:1px 3px;'>{word}</mark> "
                elif clean in real_words:
                    highlighted += f"<mark style='background:#16a34a30;color:#86efac;border-radius:3px;padding:1px 3px;'>{word}</mark> "
                else:
                    highlighted += f"{word} "

            st.markdown(f"""
            <div style='background:{card};border:1px solid {border};border-radius:12px;
                padding:20px;margin-top:16px;'>
                <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
                    text-transform:uppercase;letter-spacing:0.5px;'>🖍️ Highlighted Article</p>
                <p style='font-size:11px;color:{sub};margin:0 0 14px 0;'>
                    <span style='color:#fca5a5;'>■</span> pushes toward FAKE &nbsp;
                    <span style='color:#86efac;'>■</span> pushes toward REAL
                </p>
                <p style='font-size:13px;color:{text};line-height:1.9;margin:0;'>{highlighted}{'...' if len(inputs["article_text"]) > 800 else ''}</p>
            </div>
            """, unsafe_allow_html=True)

        return

    # ── INPUT VIEW ────────────────────────────────────────
    # On mobile show full width form, hide info panel
    st.markdown("""
    <style>
    .nc-info-panel { display: block; }
    @media (max-width: 768px) { .nc-info-panel { display: none; } }
    </style>
    """, unsafe_allow_html=True)

    col_form, col_info = st.columns([3, 1])

    with col_form:
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:14px;
            padding:24px 24px 16px 24px;box-shadow:0 2px 12px rgba(0,0,0,0.05);margin-bottom:16px;'>
            <h3 style='font-size:18px;font-weight:800;color:{text};margin:0 0 4px 0;'>Analyse an Article</h3>
            <p style='font-size:13px;color:{sub};margin:0;'>Paste text or enter a URL to scan an article instantly.</p>
        </div>
        """, unsafe_allow_html=True)

        input_mode = st.radio("Input method", ["📋 Paste Text", "🔗 Scan URL"],
                              horizontal=True, label_visibility="collapsed")

        article_text = ""
        source_url   = ""
        scraped_meta = {}

        if input_mode == "🔗 Scan URL":
            url_input = st.text_input("Article URL", placeholder="https://example.com/article-to-check")
            if url_input and st.button("🔍 Fetch Article", type="secondary"):
                with st.spinner("Fetching article..."):
                    scraped, err = scrape_url(url_input)
                if err:
                    st.error(err)
                else:
                    st.session_state["scraped_article"] = scraped
                    st.success(f"✓ Article fetched: {scraped.get('title', 'Untitled')}")

            if "scraped_article" in st.session_state and st.session_state["scraped_article"]:
                s = st.session_state["scraped_article"]
                article_text = s["text"]
                source_url   = s["source_url"]
                scraped_meta = s
                st.markdown(f"""
                <div style='background:{muted};border:1px solid {border};border-radius:10px;
                    padding:14px 16px;margin-top:8px;'>
                    <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;'>{s.get("title","")}</p>
                    <p style='font-size:11px;color:{sub};margin:0;'>{len(article_text):,} characters extracted</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            if "scraped_article" in st.session_state:
                del st.session_state["scraped_article"]
            article_text = st.text_area("Article Text *",
                                        placeholder="Paste the full article or a substantial excerpt here...",
                                        height=220, max_chars=10000)
            char_count = len(article_text)
            if char_count > 0:
                ok = char_count >= 200
                st.markdown(f"<p style='font-size:12px;color:{'#16a34a' if ok else '#f97316'};margin-top:-6px;'>"
                            f"{char_count:,} characters {'· Good length ✓' if ok else '· More text improves accuracy'}</p>",
                            unsafe_allow_html=True)
            source_url = st.text_input("Source URL (optional)", placeholder="https://example.com/article")

        st.markdown(f"<p style='font-size:13px;font-weight:600;color:{text};margin:18px 0 6px 0;'>Source Details</p>",
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            trust_score = st.slider("Trust Score", 0.0, 1.0, 0.5, 0.01,
                                    help="Domain credibility (0=untrusted, 1=trusted)")
        with c2:
            follower_count = st.number_input("Author Followers", 0, 500_000_000, 1000, 100)
        with c3:
            account_age = st.number_input("Account Age (days)", 0, 36500, 365, 1)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        clicked = st.button("🔍  Analyse Article", type="primary", use_container_width=True)

    with col_info:
        st.markdown(f"""
        <div class='nc-info-panel' style='background:{muted};border:1px solid {border};
            border-radius:12px;padding:20px;'>
            <p style='font-size:11px;font-weight:700;color:{text};margin:0 0 14px 0;text-transform:uppercase;letter-spacing:0.5px;'>How It Works</p>
            <div style='display:flex;flex-direction:column;gap:14px;'>
                <div style='display:flex;gap:12px;align-items:flex-start;'>
                    <img src='https://cdn-icons-png.flaticon.com/128/748/748035.png'
                        style='width:22px;height:22px;object-fit:contain;flex-shrink:0;margin-top:1px;filter:{F};'>
                    <p style='font-size:12px;color:{sub};margin:0;line-height:1.5;'>Paste text or enter a URL to auto-fetch the article.</p>
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
            st.error("Please enter at least 20 characters of article text.")
            return
        is_valid, errors = validate_metadata_inputs(trust_score, follower_count, account_age)
        if not is_valid:
            for e in errors:
                st.error(e)
            return

        with st.spinner("Analysing article..."):
            try:
                # Detect language and translate if needed
                lang_code, lang_name = detect_language(article_text)
                text_for_model, was_translated = translate_to_english(article_text, lang_code)
                if was_translated:
                    st.info(f"{get_language_flag(lang_code)} Detected {lang_name} — translated to English for analysis.")

                result = predict(text=text_for_model, trust_score=trust_score,
                                 follower_count=int(follower_count), account_age=int(account_age))
            except RuntimeError as e:
                st.error(str(e)); return
            except Exception as e:
                st.error(f"Analysis failed: {e}"); return

        st.session_state["detect_result"] = result
        st.session_state["detect_inputs"] = {
            "article_text":    article_text,
            "text_for_model":  text_for_model,
            "lang_code":       lang_code,
            "lang_name":       lang_name,
            "was_translated":  was_translated,
            "trust_score":     trust_score,
            "follower_count":  int(follower_count),
            "account_age":     int(account_age),
            "source_url":      source_url,
            "title":           scraped_meta.get("title", ""),
            "top_image":       scraped_meta.get("top_image", ""),
        }

        try:
            insert_detection(article_snippet=article_text, source_url=source_url or None,
                             trust_score=trust_score, follower_count=int(follower_count),
                             account_age=int(account_age), sentiment=result["sentiment"],
                             readability=result["readability"], prediction=result["prediction"],
                             confidence=result["confidence"])
        except Exception:
            pass

        if "scraped_article" in st.session_state:
            del st.session_state["scraped_article"]
        st.rerun()
