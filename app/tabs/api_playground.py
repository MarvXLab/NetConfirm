import streamlit as st
import json
import os

card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
muted  = "#162032"
green  = "#16a34a"
red    = "#dc2626"
blue   = "#3b82f6"
amber  = "#f59e0b"
purple = "#8b5cf6"

API_BASE = os.getenv("API_BASE_URL", "https://netconfirm-api.onrender.com")


def _code_block(content: str, lang: str = "json"):
    st.markdown(f"""
    <div style='background:#0d1117;border:1px solid {border};border-radius:10px;
        padding:16px;overflow-x:auto;margin-top:8px;'>
        <pre style='margin:0;font-size:12px;color:#e6edf3;font-family:monospace;
            white-space:pre-wrap;word-break:break-all;'>{content}</pre>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown(f"""
    <div style='margin-bottom:20px;'>
        <h2 style='font-size:20px;font-weight:800;color:{text};margin:0 0 4px 0;'>
            ⚡ API Playground
        </h2>
        <p style='font-size:13px;color:{sub};margin:0;'>
            Test the NetConfirm REST API, view docs, and manage your API keys.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── API base URL banner ───────────────────────────────
    st.markdown(f"""
    <div style='background:{card};border:1px solid {border};border-radius:10px;
        padding:14px 18px;margin-bottom:20px;display:flex;align-items:center;gap:12px;'>
        <span style='font-size:18px;'>🔗</span>
        <div>
            <p style='font-size:11px;color:{sub};margin:0 0 2px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>API Base URL</p>
            <p style='font-size:13px;font-weight:700;color:{blue};margin:0;font-family:monospace;'>
                {API_BASE}
            </p>
        </div>
        <div style='margin-left:auto;'>
            <a href='{API_BASE}/docs' target='_blank'
                style='font-size:12px;color:{blue};text-decoration:none;font-weight:600;'>
                📖 View Full Docs →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_test, tab_keys, tab_docs = st.tabs([
        "🧪 Test Endpoints", "🔑 API Keys", "📖 Quick Reference"
    ])

    # ════════════════════════════════════════════════════
    # TAB 1 — Test Endpoints
    # ════════════════════════════════════════════════════
    with tab_test:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        endpoint = st.selectbox("Endpoint", [
            "POST /predict — Analyse text",
            "POST /predict/url — Analyse a URL",
            "POST /predict/batch — Analyse multiple URLs",
            "GET /health — Health check",
        ], label_visibility="collapsed")

        api_key_input = st.text_input(
            "X-API-Key",
            placeholder="nc-your-api-key-here  (or your master key)",
            type="password",
        )

        st.markdown(f"<p style='font-size:12px;color:{sub};margin:4px 0 12px 0;'>"
                    f"Pass your API key in the X-API-Key header</p>",
                    unsafe_allow_html=True)

        # ── /predict ──────────────────────────────────────
        if "POST /predict" in endpoint and "url" not in endpoint and "batch" not in endpoint:
            article_text = st.text_area("Article Text *",
                                        placeholder="Paste article text here...",
                                        height=140)
            c1, c2, c3 = st.columns(3)
            with c1: trust  = st.slider("Trust Score", 0.0, 1.0, 0.5, 0.01)
            with c2: follow = st.number_input("Followers", 0, 500_000_000, 1000, 100)
            with c3: age    = st.number_input("Account Age (days)", 0, 36500, 365, 1)

            payload = {
                "text": article_text,
                "trust_score": trust,
                "follower_count": int(follow),
                "account_age": int(age),
            }
            curl = (f'curl -X POST "{API_BASE}/predict" \\\n'
                    f'  -H "X-API-Key: YOUR_KEY" \\\n'
                    f'  -H "Content-Type: application/json" \\\n'
                    f'  -d \'{json.dumps(payload, indent=2)}\'')

        # ── /predict/url ──────────────────────────────────
        elif "url" in endpoint and "batch" not in endpoint:
            url_in = st.text_input("Article URL", placeholder="https://example.com/article")
            c1, c2, c3 = st.columns(3)
            with c1: trust  = st.slider("Trust Score", 0.0, 1.0, 0.5, 0.01, key="url_trust")
            with c2: follow = st.number_input("Followers", 0, 500_000_000, 1000, 100, key="url_follow")
            with c3: age    = st.number_input("Account Age (days)", 0, 36500, 365, 1, key="url_age")

            payload = {"url": url_in, "trust_score": trust,
                       "follower_count": int(follow), "account_age": int(age)}
            curl = (f'curl -X POST "{API_BASE}/predict/url" \\\n'
                    f'  -H "X-API-Key: YOUR_KEY" \\\n'
                    f'  -H "Content-Type: application/json" \\\n'
                    f'  -d \'{json.dumps(payload)}\'')

        # ── /predict/batch ────────────────────────────────
        elif "batch" in endpoint:
            urls_raw = st.text_area("URLs (one per line, max 20)",
                                    placeholder="https://example.com/article-1\nhttps://example.com/article-2",
                                    height=120)
            c1, c2, c3 = st.columns(3)
            with c1: trust  = st.slider("Trust Score", 0.0, 1.0, 0.5, 0.01, key="b_trust")
            with c2: follow = st.number_input("Followers", 0, 500_000_000, 1000, 100, key="b_follow")
            with c3: age    = st.number_input("Account Age (days)", 0, 36500, 365, 1, key="b_age")

            urls_list = [u.strip() for u in urls_raw.splitlines() if u.strip()][:20]
            payload = {"urls": urls_list, "trust_score": trust,
                       "follower_count": int(follow), "account_age": int(age)}
            curl = (f'curl -X POST "{API_BASE}/predict/batch" \\\n'
                    f'  -H "X-API-Key: YOUR_KEY" \\\n'
                    f'  -H "Content-Type: application/json" \\\n'
                    f'  -d \'{json.dumps(payload)}\'')

        # ── /health ───────────────────────────────────────
        else:
            payload = None
            curl = f'curl "{API_BASE}/health"'

        # cURL preview
        st.markdown(f"<p style='font-size:12px;font-weight:700;color:{sub};margin:12px 0 4px 0;"
                    f"text-transform:uppercase;letter-spacing:0.5px;'>cURL Command</p>",
                    unsafe_allow_html=True)
        _code_block(curl, "bash")

        # Send request
        if st.button("▶  Send Request", type="primary", use_container_width=False):
            if not api_key_input.strip() and "health" not in endpoint:
                st.error("Enter your API key first.")
            else:
                import requests as req
                headers = {"X-API-Key": api_key_input.strip(),
                           "Content-Type": "application/json"}
                try:
                    with st.spinner("Sending request..."):
                        if payload is None:
                            r = req.get(f"{API_BASE}/health", timeout=15)
                        elif "batch" in endpoint:
                            r = req.post(f"{API_BASE}/predict/batch",
                                         json=payload, headers=headers, timeout=120)
                        elif "url" in endpoint and "batch" not in endpoint:
                            r = req.post(f"{API_BASE}/predict/url",
                                         json=payload, headers=headers, timeout=30)
                        else:
                            r = req.post(f"{API_BASE}/predict",
                                         json=payload, headers=headers, timeout=30)

                    status_color = green if r.status_code == 200 else red
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:10px;margin:12px 0 6px 0;'>
                        <span style='font-size:13px;font-weight:700;color:{status_color};'>
                            HTTP {r.status_code}
                        </span>
                        <span style='font-size:12px;color:{sub};'>
                            {r.elapsed.total_seconds()*1000:.0f}ms
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

                    try:
                        _code_block(json.dumps(r.json(), indent=2))
                    except Exception:
                        _code_block(r.text)

                except Exception as e:
                    st.error(f"Request failed: {e}")

    # ════════════════════════════════════════════════════
    # TAB 2 — API Keys
    # ════════════════════════════════════════════════════
    with tab_keys:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:12px;
            padding:20px;margin-bottom:16px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>Generate New API Key</p>
            <p style='font-size:12px;color:{sub};margin:0 0 14px 0;'>
                Keys are generated via the API itself using your master key.
                Set <code style='color:{blue};'>NETCONFIRM_API_KEY</code> on Render as your master key.
            </p>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            key_name   = st.text_input("Key name / label", placeholder="e.g. my-app, browser-ext")
            master_key = st.text_input("Master API Key", type="password",
                                       placeholder="Your NETCONFIRM_API_KEY value")
        with c2:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            gen_btn = st.button("🔑 Generate", type="primary", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if gen_btn:
            if not master_key.strip():
                st.error("Enter your master key.")
            else:
                import requests as req
                try:
                    r = req.post(
                        f"{API_BASE}/keys/generate",
                        params={"name": key_name or "default"},
                        headers={"X-API-Key": master_key.strip()},
                        timeout=15,
                    )
                    if r.status_code == 200:
                        data = r.json()
                        st.success("✓ API key generated!")
                        st.markdown(f"""
                        <div style='background:#0f2d15;border:1px solid {green}40;
                            border-radius:10px;padding:16px;margin-top:8px;'>
                            <p style='font-size:11px;color:{sub};margin:0 0 6px 0;
                                text-transform:uppercase;'>Your New API Key</p>
                            <p style='font-size:14px;font-weight:700;color:{green};
                                font-family:monospace;margin:0;word-break:break-all;'>
                                {data['api_key']}
                            </p>
                            <p style='font-size:11px;color:{amber};margin:8px 0 0 0;'>
                                ⚠ Copy this now — it will not be shown again.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Failed: {r.json().get('detail', r.text)}")
                except Exception as e:
                    st.error(f"Request failed: {e}")

        # How to use
        st.markdown(f"""
        <div style='background:{muted};border:1px solid {border};border-radius:12px;
            padding:20px;margin-top:8px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 12px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>How to Use Your Key</p>
            <p style='font-size:12px;color:{sub};margin:0 0 8px 0;'>
                Pass it in every request as the <code style='color:{blue};'>X-API-Key</code> header:
            </p>
        """, unsafe_allow_html=True)
        _code_block('curl -H "X-API-Key: nc-your-key-here" ' + f'"{API_BASE}/predict" ...')
        st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # TAB 3 — Quick Reference
    # ════════════════════════════════════════════════════
    with tab_docs:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        endpoints = [
            ("GET",  "/health",         "No auth required",  green,  "Check API health and model status"),
            ("POST", "/predict",        "X-API-Key required", amber, "Analyse article text"),
            ("POST", "/predict/url",    "X-API-Key required", amber, "Fetch and analyse a URL"),
            ("POST", "/predict/batch",  "X-API-Key required", amber, "Analyse up to 20 URLs"),
            ("POST", "/keys/generate",  "Master key required", red,  "Generate a new API key"),
        ]

        for method, path, auth, color, desc in endpoints:
            st.markdown(f"""
            <div style='background:{card};border:1px solid {border};border-radius:10px;
                padding:14px 18px;margin-bottom:8px;display:flex;align-items:center;gap:14px;'>
                <span style='font-size:11px;font-weight:800;color:{color};background:{color}22;
                    padding:3px 10px;border-radius:4px;font-family:monospace;min-width:44px;
                    text-align:center;'>{method}</span>
                <span style='font-size:13px;font-weight:700;color:{text};
                    font-family:monospace;'>{path}</span>
                <span style='font-size:11px;color:{sub};margin-left:auto;'>{auth}</span>
            </div>
            <p style='font-size:12px;color:{sub};margin:-4px 0 8px 18px;'>{desc}</p>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:{muted};border:1px solid {border};border-radius:12px;
            padding:20px;margin-top:8px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 10px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>Example Response — /predict</p>
        """, unsafe_allow_html=True)

        example = {
            "prediction": "FAKE",
            "confidence": 0.9123,
            "fake_prob": 0.9123,
            "real_prob": 0.0877,
            "sentiment": 0.312,
            "readability": 0.45,
            "language": "English",
            "translated": False,
            "analysed_at": "2025-01-15T10:30:00+00:00",
        }
        _code_block(json.dumps(example, indent=2))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <p style='font-size:12px;color:{sub};margin-top:16px;'>
            Full interactive docs available at
            <a href='{API_BASE}/docs' target='_blank'
                style='color:{blue};'>{API_BASE}/docs</a>
            (Swagger UI) and
            <a href='{API_BASE}/redoc' target='_blank'
                style='color:{blue};'>{API_BASE}/redoc</a>
            (ReDoc).
        </p>
        """, unsafe_allow_html=True)
