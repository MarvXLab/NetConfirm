import streamlit as st
import pandas as pd
import time
from ml.predict import predict
from ml.metadata_encoder import validate_metadata_inputs
from ml.translator import detect_language, translate_to_english, get_language_flag
from db.queries import insert_detection

card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
muted  = "#162032"
accent = "#1a1a2e"

MAX_URLS = 20


def scrape_url(url: str):
    try:
        from newspaper import Article
        a = Article(url, request_timeout=10)
        a.download()
        a.parse()
        if not a.text or len(a.text.strip()) < 50:
            return None, "Could not extract article text"
        return {"text": a.text, "title": a.title or url, "source_url": url}, None
    except Exception as e:
        return None, str(e)


def render():
    st.markdown(f"""
    <div style='margin-bottom:20px;'>
        <h2 style='font-size:20px;font-weight:800;color:{text};margin:0 0 4px 0;'>Batch URL Scanner</h2>
        <p style='font-size:13px;color:{sub};margin:0;'>
            Paste up to {MAX_URLS} URLs (one per line) — NetConfirm will fetch and analyse each article automatically.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Input panel ───────────────────────────────────────
    st.markdown(f"""
    <div style='background:{card};border:1px solid {border};border-radius:14px;
        padding:24px;margin-bottom:20px;'>
        <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 10px 0;
            text-transform:uppercase;letter-spacing:0.5px;'>Paste URLs</p>
    """, unsafe_allow_html=True)

    urls_input = st.text_area(
        "urls",
        placeholder="https://example.com/article-1\nhttps://example.com/article-2\nhttps://example.com/article-3",
        height=180,
        label_visibility="collapsed",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        trust_score = st.slider("Default Trust Score", 0.0, 1.0, 0.5, 0.01,
                                help="Applied to all URLs unless overridden")
    with c2:
        follower_count = st.number_input("Author Followers", 0, 500_000_000, 1000, 100)
    with c3:
        account_age = st.number_input("Account Age (days)", 0, 36500, 365, 1)

    st.markdown("</div>", unsafe_allow_html=True)

    col_btn, col_clear, _ = st.columns([2, 1, 4])
    with col_btn:
        run = st.button("🚀  Scan All URLs", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🗑 Clear", type="secondary", use_container_width=True):
            st.session_state.pop("batch_results", None)
            st.rerun()

    # ── Run batch ─────────────────────────────────────────
    if run:
        raw_urls = [u.strip() for u in urls_input.strip().splitlines() if u.strip()]
        if not raw_urls:
            st.error("Please paste at least one URL.")
            return
        if len(raw_urls) > MAX_URLS:
            st.warning(f"Only the first {MAX_URLS} URLs will be processed.")
            raw_urls = raw_urls[:MAX_URLS]

        is_valid, errors = validate_metadata_inputs(trust_score, follower_count, account_age)
        if not is_valid:
            for e in errors:
                st.error(e)
            return

        results = []
        progress_bar = st.progress(0, text="Starting...")
        status_box   = st.empty()

        for i, url in enumerate(raw_urls):
            pct  = int((i / len(raw_urls)) * 100)
            progress_bar.progress(pct, text=f"Processing {i+1}/{len(raw_urls)}...")
            status_box.markdown(
                f"<p style='font-size:12px;color:{sub};'>🔗 Fetching: {url[:80]}{'...' if len(url)>80 else ''}</p>",
                unsafe_allow_html=True,
            )

            scraped, err = scrape_url(url)
            if err or not scraped:
                results.append({
                    "url": url, "title": "—", "verdict": "ERROR",
                    "confidence": "—", "fake_prob": "—", "real_prob": "—",
                    "error": err or "Unknown error",
                })
                continue

            try:
                lang_code, lang_name = detect_language(scraped["text"])
                text_for_model, _ = translate_to_english(scraped["text"], lang_code)
                lang_badge = f"{get_language_flag(lang_code)} {lang_name}" if lang_code != "en" else "🇬🇧 English"

                result = predict(
                    text=text_for_model,
                    trust_score=trust_score,
                    follower_count=int(follower_count),
                    account_age=int(account_age),
                )
                results.append({
                    "url":        url,
                    "title":      scraped["title"][:80],
                    "verdict":    result["prediction"],
                    "confidence": f"{result['confidence']*100:.1f}%",
                    "fake_prob":  f"{result['fake_prob']*100:.1f}%",
                    "real_prob":  f"{result['real_prob']*100:.1f}%",
                    "language":   lang_badge,
                    "error":      "",
                })
                try:
                    insert_detection(
                        article_snippet=scraped["text"], source_url=url,
                        trust_score=trust_score, follower_count=int(follower_count),
                        account_age=int(account_age), sentiment=result["sentiment"],
                        readability=result["readability"], prediction=result["prediction"],
                        confidence=result["confidence"],
                    )
                except Exception:
                    pass
            except Exception as e:
                results.append({
                    "url": url, "title": scraped["title"][:80], "verdict": "ERROR",
                    "confidence": "—", "fake_prob": "—", "real_prob": "—",
                    "language": "", "error": str(e),
                })

            time.sleep(0.3)  # polite delay between requests

        progress_bar.progress(100, text="Done!")
        status_box.empty()
        st.session_state["batch_results"] = results

    # ── Results ───────────────────────────────────────────
    if "batch_results" in st.session_state and st.session_state["batch_results"]:
        results = st.session_state["batch_results"]

        total  = len(results)
        fakes  = sum(1 for r in results if r["verdict"] == "FAKE")
        reals  = sum(1 for r in results if r["verdict"] == "REAL")
        errors = sum(1 for r in results if r["verdict"] == "ERROR")

        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        for col, label, val, color in [
            (m1, "Total Scanned", total,  text),
            (m2, "Fake Detected", fakes,  "#dc2626"),
            (m3, "Real Verified", reals,  "#16a34a"),
            (m4, "Errors",        errors, "#f59e0b"),
        ]:
            col.markdown(f"""
            <div style='background:{card};border:1px solid {border};border-radius:10px;
                padding:16px 20px;text-align:center;'>
                <p style='font-size:11px;color:{sub};margin:0 0 4px 0;text-transform:uppercase;
                    letter-spacing:0.5px;'>{label}</p>
                <p style='font-size:28px;font-weight:800;color:{color};margin:0;'>{val}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # Results table
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:14px;
            padding:20px;margin-bottom:16px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 16px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>Scan Results</p>
        """, unsafe_allow_html=True)

        for r in results:
            if r["verdict"] == "FAKE":
                v_color, v_bg, v_icon = "#dc2626", "#2d1515", "⚠️"
            elif r["verdict"] == "REAL":
                v_color, v_bg, v_icon = "#16a34a", "#0f2d15", "✅"
            else:
                v_color, v_bg, v_icon = "#f59e0b", "#2d2510", "❌"

            err_html = f"<p style='font-size:11px;color:#f59e0b;margin:4px 0 0 0;'>{r['error']}</p>" if r["error"] else ""
            conf_html = (
                f"<span style='font-size:12px;font-weight:700;color:{v_color};'>{r['confidence']}</span>"
                f"<span style='font-size:11px;color:{sub};'> · fake {r['fake_prob']} · real {r['real_prob']}</span>"
                if r["verdict"] != "ERROR" else ""
            )

            st.markdown(f"""
            <div style='background:{v_bg};border:1px solid {v_color}30;border-left:4px solid {v_color};
                border-radius:10px;padding:14px 16px;margin-bottom:10px;'>
                <div style='display:flex;align-items:flex-start;justify-content:space-between;gap:12px;'>
                    <div style='flex:1;min-width:0;'>
                        <p style='font-size:13px;font-weight:600;color:{text};margin:0 0 3px 0;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{r['title']}</p>
                        <p style='font-size:11px;color:{sub};margin:0;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{r['url']}</p>
                        {f"<p style='font-size:11px;color:#93c5fd;margin:3px 0 0 0;'>{r.get('language','')}</p>" if r.get('language') else ''}
                        {err_html}
                    </div>
                    <div style='text-align:right;flex-shrink:0;'>
                        <div style='font-size:14px;font-weight:800;color:{v_color};'>{v_icon} {r['verdict']}</div>
                        {conf_html}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # CSV download
        df_export = pd.DataFrame([{
            "URL":        r["url"],
            "Title":      r["title"],
            "Verdict":    r["verdict"],
            "Confidence": r["confidence"],
            "Fake Prob":  r["fake_prob"],
            "Real Prob":  r["real_prob"],
            "Language":   r.get("language", ""),
            "Error":      r["error"],
        } for r in results])

        st.download_button(
            label="⬇️  Download Results as CSV",
            data=df_export.to_csv(index=False).encode("utf-8"),
            file_name="netconfirm_batch_results.csv",
            mime="text/csv",
            type="secondary",
        )
