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

API_BASE = os.getenv("API_BASE_URL", "https://netconfirm-api.onrender.com")


def _code_block(content: str):
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
            Get a free API key, test endpoints, and integrate NetConfirm into your apps.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # API base URL banner
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

    tab_getkey, tab_lookup, tab_test, tab_docs = st.tabs([
        "🔑 Get Free API Key", "🔎 Look Up My Key", "🧪 Test Endpoints", "📖 Quick Reference"
    ])

    # ── TAB 1: Get Free API Key ───────────────────────────
    with tab_getkey:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:12px;
            padding:24px;margin-bottom:16px;'>
            <p style='font-size:16px;font-weight:800;color:{text};margin:0 0 6px 0;'>
                Get Your Free API Key
            </p>
            <p style='font-size:13px;color:{sub};margin:0 0 20px 0;'>
                No account needed — just enter your email and name. One key per email.
                Re-registering with the same email replaces your old key.
            </p>
        """, unsafe_allow_html=True)

        reg_email = st.text_input("Your Email *", placeholder="you@example.com", key="reg_email")
        reg_name  = st.text_input("Your Name / App Name", placeholder="e.g. John, my-news-app", key="reg_name")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🔑  Generate My Free API Key", type="primary", use_container_width=True):
            if not reg_email.strip():
                st.error("Please enter your email address.")
            else:
                import requests as req
                try:
                    with st.spinner("Generating your key..."):
                        r = req.post(
                            f"{API_BASE}/keys/register",
                            params={"email": reg_email.strip(), "name": reg_name.strip() or "default"},
                            timeout=15,
                        )
                    if r.status_code == 200:
                        data = r.json()
                        st.success("✓ Your API key has been generated!")
                        st.markdown(f"""
                        <div style='background:#0f2d15;border:1px solid {green}40;
                            border-radius:12px;padding:20px;margin-top:8px;'>
                            <p style='font-size:11px;color:{sub};margin:0 0 8px 0;
                                text-transform:uppercase;letter-spacing:0.5px;'>Your API Key</p>
                            <p style='font-size:15px;font-weight:700;color:{green};
                                font-family:monospace;margin:0 0 12px 0;word-break:break-all;'>
                                {data['api_key']}
                            </p>
                            <p style='font-size:11px;color:{amber};margin:0 0 12px 0;'>
                                ⚠ Copy this now — it will not be shown again.
                                If you lose it, re-register with the same email to get a new one.
                            </p>
                            <p style='font-size:11px;color:{sub};margin:0;'>
                                Registered to: <strong style='color:{text};'>{data['email']}</strong>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"<p style='font-size:12px;font-weight:700;color:{sub};"
                                    f"margin:16px 0 6px 0;text-transform:uppercase;'>How to use it:</p>",
                                    unsafe_allow_html=True)
                        _code_block(
                            f'curl -X POST "{API_BASE}/predict" \\\n'
                            f'  -H "X-API-Key: {data["api_key"]}" \\\n'
                            f'  -H "Content-Type: application/json" \\\n'
                            f'  -d \'{{"text": "Your article text here..."}}\''
                        )
                    else:
                        err = r.json().get("detail", r.text)
                        st.error(f"Failed: {err}")
                except Exception as e:
                    st.error(f"Could not reach API: {e}. Make sure the API service is running.")

        # How it works
        st.markdown(f"""
        <div style='background:{muted};border:1px solid {border};border-radius:12px;
            padding:20px;margin-top:16px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 12px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>How API Keys Work</p>
            <div style='display:flex;flex-direction:column;gap:10px;'>
                <div style='display:flex;gap:10px;'>
                    <span style='color:{green};font-weight:700;'>1.</span>
                    <p style='font-size:12px;color:{sub};margin:0;'>Enter your email above and click Generate</p>
                </div>
                <div style='display:flex;gap:10px;'>
                    <span style='color:{green};font-weight:700;'>2.</span>
                    <p style='font-size:12px;color:{sub};margin:0;'>Copy your key — it is only shown once</p>
                </div>
                <div style='display:flex;gap:10px;'>
                    <span style='color:{green};font-weight:700;'>3.</span>
                    <p style='font-size:12px;color:{sub};margin:0;'>
                        Pass it in every API request as the
                        <code style='color:{blue};background:#0f172a;padding:1px 5px;border-radius:3px;'>
                        X-API-Key</code> header
                    </p>
                </div>
                <div style='display:flex;gap:10px;'>
                    <span style='color:{green};font-weight:700;'>4.</span>
                    <p style='font-size:12px;color:{sub};margin:0;'>
                        Lost your key? Re-register with the same email to get a new one
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TAB 2: Look Up My Key ─────────────────────────────
    with tab_lookup:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:12px;
            padding:20px;margin-bottom:16px;'>
            <p style='font-size:13px;font-weight:700;color:{text};margin:0 0 4px 0;'>
                Check your key status and usage
            </p>
            <p style='font-size:12px;color:{sub};margin:0 0 14px 0;'>
                Enter the email you registered with. Your raw key is never returned here.
            </p>
        """, unsafe_allow_html=True)
        lookup_email = st.text_input("Registered Email", placeholder="you@example.com", key="lookup_email")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🔎  Look Up", type="primary"):
            if not lookup_email.strip():
                st.error("Enter your email.")
            else:
                import requests as req
                try:
                    with st.spinner("Looking up..."):
                        r = req.get(f"{API_BASE}/keys/lookup",
                                    params={"email": lookup_email.strip()}, timeout=10)
                    if r.status_code == 200:
                        d = r.json()
                        st.markdown(f"""
                        <div style='background:{card};border:1px solid {green}40;
                            border-left:4px solid {green};border-radius:12px;padding:20px;'>
                            <p style='font-size:14px;font-weight:700;color:{text};margin:0 0 14px 0;'>
                                ✓ Key found for {d['email']}
                            </p>
                            <div style='display:grid;grid-template-columns:1fr 1fr;gap:12px;'>
                                <div>
                                    <p style='font-size:10px;color:{sub};margin:0 0 2px 0;
                                        text-transform:uppercase;'>Key Prefix</p>
                                    <p style='font-size:13px;font-weight:700;color:{blue};
                                        font-family:monospace;margin:0;'>{d['key_prefix']}</p>
                                </div>
                                <div>
                                    <p style='font-size:10px;color:{sub};margin:0 0 2px 0;
                                        text-transform:uppercase;'>Status</p>
                                    <p style='font-size:13px;font-weight:700;
                                        color:{"#16a34a" if d["active"] else "#dc2626"};margin:0;'>
                                        {"Active" if d["active"] else "Revoked"}</p>
                                </div>
                                <div>
                                    <p style='font-size:10px;color:{sub};margin:0 0 2px 0;
                                        text-transform:uppercase;'>Total Requests</p>
                                    <p style='font-size:13px;font-weight:700;color:{text};margin:0;'>
                                        {d['requests']:,}</p>
                                </div>
                                <div>
                                    <p style='font-size:10px;color:{sub};margin:0 0 2px 0;
                                        text-transform:uppercase;'>Last Used</p>
                                    <p style='font-size:13px;font-weight:700;color:{text};margin:0;'>
                                        {d['last_used'][:10] if d['last_used'] else 'Never'}</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    elif r.status_code == 404:
                        st.warning("No key found for this email. Register above to get one.")
                    else:
                        st.error(r.json().get("detail", r.text))
                except Exception as e:
                    st.error(f"Request failed: {e}")

    # ── TAB 3: Test Endpoints ─────────────────────────────
    with tab_test:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        endpoint = st.selectbox("Endpoint", [
            "POST /predict — Analyse text",
            "POST /predict/url — Analyse a URL",
            "POST /predict/batch — Analyse multiple URLs",
            "GET /health — Health check",
        ], label_visibility="collapsed")

        api_key_input = st.text_input("X-API-Key", placeholder="nc-your-api-key-here",
                                      type="password")
        st.markdown(f"<p style='font-size:12px;color:{sub};margin:4px 0 12px 0;'>"
                    f"Get your free key in the 🔑 Get Free API Key tab</p>",
                    unsafe_allow_html=True)

        if "POST /predict" in endpoint and "url" not in endpoint and "batch" not in endpoint:
            article_text = st.text_area("Article Text *", placeholder="Paste article text here...", height=140)
            c1, c2, c3 = st.columns(3)
            with c1: trust  = st.slider("Trust Score", 0.0, 1.0, 0.5, 0.01)
            with c2: follow = st.number_input("Followers", 0, 500_000_000, 1000, 100)
            with c3: age    = st.number_input("Account Age (days)", 0, 36500, 365, 1)
            payload = {"text": article_text, "trust_score": trust,
                       "follower_count": int(follow), "account_age": int(age)}
            curl = (f'curl -X POST "{API_BASE}/predict" \\\n'
                    f'  -H "X-API-Key: YOUR_KEY" \\\n'
                    f'  -H "Content-Type: application/json" \\\n'
                    f'  -d \'{json.dumps(payload, indent=2)}\'')

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
        else:
            payload = None
            curl = f'curl "{API_BASE}/health"'

        st.markdown(f"<p style='font-size:12px;font-weight:700;color:{sub};margin:12px 0 4px 0;"
                    f"text-transform:uppercase;letter-spacing:0.5px;'>cURL Command</p>",
                    unsafe_allow_html=True)
        _code_block(curl)

        if st.button("▶  Send Request", type="primary"):
            if not api_key_input.strip() and "health" not in endpoint:
                st.error("Enter your API key first.")
            else:
                import requests as req
                headers = {"X-API-Key": api_key_input.strip(), "Content-Type": "application/json"}
                try:
                    with st.spinner("Sending request..."):
                        if payload is None:
                            r = req.get(f"{API_BASE}/health", timeout=15)
                        elif "batch" in endpoint:
                            r = req.post(f"{API_BASE}/predict/batch", json=payload, headers=headers, timeout=120)
                        elif "url" in endpoint and "batch" not in endpoint:
                            r = req.post(f"{API_BASE}/predict/url", json=payload, headers=headers, timeout=30)
                        else:
                            r = req.post(f"{API_BASE}/predict", json=payload, headers=headers, timeout=30)

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

    # ── TAB 4: Quick Reference ────────────────────────────
    with tab_docs:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        endpoints = [
            ("GET",  "/health",          "No auth required",   green, "Check API health and model status"),
            ("POST", "/keys/register",   "No auth required",   green, "Get a free API key with your email"),
            ("GET",  "/keys/lookup",     "No auth required",   green, "Check your key status and usage"),
            ("POST", "/predict",         "X-API-Key required", amber, "Analyse article text"),
            ("POST", "/predict/url",     "X-API-Key required", amber, "Fetch and analyse a URL"),
            ("POST", "/predict/batch",   "X-API-Key required", amber, "Analyse up to 20 URLs"),
            ("POST", "/keys/generate",   "Master key required", red,  "Admin: generate a key"),
        ]

        for method, path, auth, color, desc in endpoints:
            st.markdown(f"""
            <div style='background:{card};border:1px solid {border};border-radius:10px;
                padding:14px 18px;margin-bottom:6px;display:flex;align-items:center;gap:14px;'>
                <span style='font-size:11px;font-weight:800;color:{color};background:{color}22;
                    padding:3px 10px;border-radius:4px;font-family:monospace;min-width:44px;
                    text-align:center;'>{method}</span>
                <span style='font-size:13px;font-weight:700;color:{text};
                    font-family:monospace;'>{path}</span>
                <span style='font-size:11px;color:{sub};margin-left:auto;'>{auth}</span>
            </div>
            <p style='font-size:12px;color:{sub};margin:-2px 0 10px 18px;'>{desc}</p>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:{muted};border:1px solid {border};border-radius:12px;
            padding:20px;margin-top:8px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 10px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>Example Response — /predict</p>
        """, unsafe_allow_html=True)

        _code_block(json.dumps({
            "prediction": "FAKE", "confidence": 0.9123,
            "fake_prob": 0.9123, "real_prob": 0.0877,
            "sentiment": 0.312, "readability": 0.45,
            "language": "English", "translated": False,
            "analysed_at": "2025-01-15T10:30:00+00:00",
        }, indent=2))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <p style='font-size:12px;color:{sub};margin-top:16px;'>
            Full interactive docs at
            <a href='{API_BASE}/docs' target='_blank' style='color:{blue};'>{API_BASE}/docs</a>
            (Swagger UI) and
            <a href='{API_BASE}/redoc' target='_blank' style='color:{blue};'>{API_BASE}/redoc</a>
            (ReDoc).
        </p>
        """, unsafe_allow_html=True)
