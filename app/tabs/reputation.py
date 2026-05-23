import streamlit as st
from db.queries import (
    search_domains, get_domain, upsert_domain,
    flag_domain, sync_domain_stats, get_reputation_stats,
)

card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
muted  = "#162032"
red    = "#dc2626"
green  = "#16a34a"
amber  = "#f59e0b"
blue   = "#3b82f6"

REP_ICON      = "https://cdn-icons-png.flaticon.com/128/8915/8915911.png"
NO_DOM_ICON   = "https://cdn-icons-png.flaticon.com/128/3434/3434892.png"
LOOKUP_ICON   = "https://cdn-icons-png.flaticon.com/128/15714/15714705.png"
SUBMIT_ICON   = "https://cdn-icons-png.flaticon.com/128/14964/14964596.png"
FLAG_ICON     = "https://cdn-icons-png.flaticon.com/128/16973/16973545.png"
DB_ICON       = "https://cdn-icons-png.flaticon.com/128/2232/2232186.png"

              "Sports", "Science", "Health", "Business", "Satire", "Conspiracy"]


def _trust_color(score: float):
    if score >= 0.7:
        return green
    if score >= 0.4:
        return amber
    return red


def _trust_label(score: float):
    if score >= 0.7:
        return "Trusted"
    if score >= 0.4:
        return "Uncertain"
    return "Untrusted"


def render():
    st.markdown(f"""
    <div style='margin-bottom:20px;display:flex;align-items:center;gap:10px;'>
        <img src='{REP_ICON}' style='width:24px;height:24px;object-fit:contain;filter:brightness(0) invert(1);'>
        <div>
            <h2 style='font-size:20px;font-weight:800;color:{text};margin:0 0 2px 0;display:flex;align-items:center;gap:8px;'>
                <img src='{DB_ICON}' style='width:18px;height:18px;object-fit:contain;filter:brightness(0) invert(1);'>
                Source Reputation Database
            </h2>
            <p style='font-size:13px;color:{sub};margin:0;'>Search, rate and flag news domains. Community-powered trust registry.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Auto-sync domain stats from detections
    try:
        sync_domain_stats()
    except Exception:
        pass

    # ── Summary stats ─────────────────────────────────────
    try:
        stats = get_reputation_stats()
    except Exception:
        stats = None

    if stats and stats["total_domains"]:
        m1, m2, m3, m4, m5 = st.columns(5)
        for col, label, val, color in [
            (m1, "Total Domains",   int(stats["total_domains"]),   text),
            (m2, "Trusted",         int(stats["trusted_count"] or 0),   green),
            (m3, "Untrusted",       int(stats["untrusted_count"] or 0), red),
            (m4, "Flagged",         int(stats["flagged_count"] or 0),   amber),
            (m5, "Avg Trust Score", f"{float(stats['avg_trust'] or 0):.2f}", blue),
        ]:
            col.markdown(f"""
            <div style='background:{card};border:1px solid {border};border-radius:10px;
                padding:14px;text-align:center;margin-bottom:16px;'>
                <p style='font-size:11px;color:{sub};margin:0 0 4px 0;
                    text-transform:uppercase;letter-spacing:0.5px;'>{label}</p>
                <p style='font-size:24px;font-weight:800;color:{color};margin:0;'>{val}</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Tabs: Search | Lookup | Submit | Flag ─────────────
    tab_search, tab_lookup, tab_submit, tab_flag = st.tabs([
        "Search Registry", "Look Up Domain", "Submit Domain", "Flag Domain"
    ])

    # ════════════════════════════════════════════════════
    # TAB 1 — Search Registry
    # ════════════════════════════════════════════════════
    with tab_search:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col_q, col_f = st.columns([3, 1])
        with col_q:
            query = st.text_input("Search domains", placeholder="e.g. bbc, cnn, politics...",
                                  label_visibility="collapsed")
        with col_f:
            show_flagged = st.checkbox("Flagged only", value=False)

        try:
            domains = search_domains(query=query, limit=50)
            if show_flagged:
                domains = [d for d in domains if d["flagged"]]
        except Exception as e:
            st.error(f"Could not load registry: {e}")
            domains = []

        if not domains:
            st.markdown(f"""
            <div style='background:{muted};border:1px solid {border};border-radius:12px;
                padding:40px;text-align:center;margin-top:12px;'>
                <img src='{NO_DOM_ICON}' style='width:40px;height:40px;object-fit:contain;
                    filter:brightness(0) invert(1);opacity:0.5;display:block;margin:0 auto 12px auto;'>
                <p style='font-size:14px;color:{sub};margin:0;'>
                    No domains found. Submit articles with source URLs to auto-populate,
                    or add domains manually using the Submit tab.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='font-size:12px;color:{sub};margin:8px 0 12px 0;'>"
                        f"{len(domains)} domain{'s' if len(domains)!=1 else ''} found</p>",
                        unsafe_allow_html=True)

            for d in domains:
                t_score  = float(d["trust_score"] or 0.5)
                t_color  = _trust_color(t_score)
                t_label  = _trust_label(t_score)
                fake_c   = int(d["fake_count"] or 0)
                real_c   = int(d["real_count"] or 0)
                total_c  = int(d["total_scans"] or 0)
                fake_pct = round(fake_c / total_c * 100) if total_c else 0
                flag_html = (f"<span style='background:{amber}22;color:{amber};font-size:10px;"
                             f"font-weight:700;padding:2px 8px;border-radius:4px;margin-left:8px;'>"
                             f"🚩 FLAGGED</span>") if d["flagged"] else ""
                desc_html = (f"<p style='font-size:11px;color:{sub};margin:4px 0 0 0;'>"
                             f"{d['description']}</p>") if d.get("description") else ""

                st.markdown(f"""
                <div style='background:{card};border:1px solid {border};border-radius:12px;
                    padding:16px 20px;margin-bottom:10px;'>
                    <div style='display:flex;align-items:center;justify-content:space-between;'>
                        <div style='flex:1;'>
                            <div style='display:flex;align-items:center;gap:8px;'>
                                <span style='font-size:14px;font-weight:700;color:{text};'>{d['domain']}</span>
                                <span style='font-size:10px;color:{sub};background:{muted};
                                    padding:2px 8px;border-radius:4px;'>{d['category'] or 'Unknown'}</span>
                                <span style='font-size:10px;color:{sub};'>{d['country'] or ''}</span>
                                {flag_html}
                            </div>
                            {desc_html}
                            <div style='display:flex;gap:16px;margin-top:8px;'>
                                <span style='font-size:11px;color:{red};'>⚠ {fake_c} fake</span>
                                <span style='font-size:11px;color:{green};'>✓ {real_c} real</span>
                                <span style='font-size:11px;color:{sub};'>{total_c} total scans</span>
                                <span style='font-size:11px;color:{amber};'>{fake_pct}% fake rate</span>
                            </div>
                        </div>
                        <div style='text-align:right;flex-shrink:0;margin-left:20px;'>
                            <div style='font-size:22px;font-weight:800;color:{t_color};'>{t_score:.2f}</div>
                            <div style='font-size:11px;color:{t_color};font-weight:600;'>{t_label}</div>
                            <div style='background:{border};border-radius:4px;height:4px;width:80px;margin-top:6px;'>
                                <div style='background:{t_color};border-radius:4px;height:4px;
                                    width:{int(t_score*80)}px;'></div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # TAB 2 — Lookup single domain
    # ════════════════════════════════════════════════════
    with tab_lookup:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col_in, col_btn = st.columns([4, 1])
        with col_in:
            lookup_domain = st.text_input("Domain to look up",
                                          placeholder="e.g. bbc.com",
                                          label_visibility="collapsed")
        with col_btn:
            do_lookup = st.button("Look Up", type="primary", use_container_width=True)

        if do_lookup and lookup_domain.strip():
            domain_clean = lookup_domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
            try:
                record = get_domain(domain_clean)
            except Exception as e:
                st.error(f"Lookup failed: {e}")
                record = None

            if record:
                t_score = float(record["trust_score"] or 0.5)
                t_color = _trust_color(t_score)
                t_label = _trust_label(t_score)
                fake_c  = int(record["fake_count"] or 0)
                real_c  = int(record["real_count"] or 0)
                total_c = int(record["total_scans"] or 0)

                st.markdown(f"""
                <div style='background:{card};border:1px solid {t_color}60;border-left:5px solid {t_color};
                    border-radius:12px;padding:24px;margin-top:12px;'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                        <div>
                            <p style='font-size:20px;font-weight:800;color:{text};margin:0 0 4px 0;'>
                                {record['domain']}
                            </p>
                            <p style='font-size:12px;color:{sub};margin:0;'>
                                {record['category'] or 'Unknown'} · {record['country'] or 'Unknown'}
                            </p>
                            <p style='font-size:12px;color:{sub};margin:8px 0 0 0;'>
                                {record['description'] or 'No description available.'}
                            </p>
                        </div>
                        <div style='text-align:right;'>
                            <div style='font-size:36px;font-weight:800;color:{t_color};'>{t_score:.2f}</div>
                            <div style='font-size:13px;color:{t_color};font-weight:700;'>{t_label}</div>
                        </div>
                    </div>
                    <div style='display:flex;gap:24px;margin-top:20px;padding-top:16px;
                        border-top:1px solid {border};'>
                        <div style='text-align:center;'>
                            <p style='font-size:22px;font-weight:800;color:{red};margin:0;'>{fake_c}</p>
                            <p style='font-size:11px;color:{sub};margin:0;'>Fake Detected</p>
                        </div>
                        <div style='text-align:center;'>
                            <p style='font-size:22px;font-weight:800;color:{green};margin:0;'>{real_c}</p>
                            <p style='font-size:11px;color:{sub};margin:0;'>Real Verified</p>
                        </div>
                        <div style='text-align:center;'>
                            <p style='font-size:22px;font-weight:800;color:{text};margin:0;'>{total_c}</p>
                            <p style='font-size:11px;color:{sub};margin:0;'>Total Scans</p>
                        </div>
                        <div style='text-align:center;'>
                            <p style='font-size:22px;font-weight:800;color:{amber};margin:0;'>
                                {'🚩' if record['flagged'] else '✓'}
                            </p>
                            <p style='font-size:11px;color:{sub};margin:0;'>
                                {'Flagged' if record['flagged'] else 'Clean'}
                            </p>
                        </div>
                    </div>
                    {f"<p style='font-size:11px;color:{amber};margin-top:12px;'>🚩 {record['flagged_reason']}</p>" if record['flagged'] else ''}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:{muted};border:1px solid {border};border-radius:12px;
                    padding:32px;text-align:center;margin-top:12px;'>
                    <img src='{NO_DOM_ICON}' style='width:36px;height:36px;object-fit:contain;
                        filter:brightness(0) invert(1);opacity:0.5;display:block;margin:0 auto 10px auto;'>
                    <p style='font-size:14px;color:{text};font-weight:600;margin:0 0 4px 0;'>
                        {domain_clean} not found
                    </p>
                    <p style='font-size:12px;color:{sub};margin:0;'>
                        This domain has no record yet. Submit it using the Submit tab.
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # TAB 3 — Submit domain
    # ════════════════════════════════════════════════════
    with tab_submit:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:12px;
            padding:20px;margin-bottom:16px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 12px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>Add or Update a Domain</p>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            new_domain = st.text_input("Domain *", placeholder="e.g. bbc.com")
            new_category = st.selectbox("Category", CATEGORIES)
        with c2:
            new_trust = st.slider("Trust Score", 0.0, 1.0, 0.5, 0.01,
                                  help="0 = completely untrusted, 1 = fully trusted")
            new_country = st.text_input("Country", placeholder="e.g. United Kingdom")

        new_desc = st.text_area("Description (optional)",
                                placeholder="Brief description of this source...",
                                height=80)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Submit Domain", type="primary"):
            if not new_domain.strip():
                st.error("Domain name is required.")
            else:
                domain_clean = new_domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
                try:
                    upsert_domain(domain_clean, new_trust, new_category,
                                  new_country or "Unknown", new_desc or "")
                    st.success(f"✓ {domain_clean} submitted successfully!")
                except Exception as e:
                    st.error(f"Failed to submit: {e}")

    # ════════════════════════════════════════════════════
    # TAB 4 — Flag domain
    # ════════════════════════════════════════════════════
    with tab_flag:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:12px;
            padding:20px;margin-bottom:16px;'>
            <p style='font-size:12px;font-weight:700;color:{text};margin:0 0 4px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>🚩 Flag a Suspicious Domain</p>
            <p style='font-size:12px;color:{sub};margin:0 0 16px 0;'>
                Report a domain that consistently publishes misinformation.
            </p>
        """, unsafe_allow_html=True)

        flag_domain_input = st.text_input("Domain to flag *", placeholder="e.g. fakenews-site.com")
        flag_reason = st.text_area("Reason *",
                                   placeholder="Describe why this domain should be flagged...",
                                   height=100)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Submit Flag", type="primary"):
            if not flag_domain_input.strip():
                st.error("Domain name is required.")
            elif not flag_reason.strip():
                st.error("Please provide a reason for flagging.")
            else:
                domain_clean = flag_domain_input.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
                try:
                    # Ensure domain exists first
                    existing = get_domain(domain_clean)
                    if not existing:
                        upsert_domain(domain_clean, 0.2, "Unknown", "Unknown", "")
                    flag_domain(domain_clean, flag_reason.strip())
                    st.success(f"✓ {domain_clean} has been flagged.")
                    st.markdown(f"""
                    <div style='background:#2d1515;border:1px solid {red}40;border-radius:10px;
                        padding:14px 16px;margin-top:8px;'>
                        <p style='font-size:13px;color:{red};font-weight:600;margin:0 0 4px 0;'>
                            🚩 {domain_clean} flagged
                        </p>
                        <p style='font-size:12px;color:{sub};margin:0;'>{flag_reason}</p>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Failed to flag domain: {e}")
