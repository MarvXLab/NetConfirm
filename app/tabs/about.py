import streamlit as st

ABOUT_ICON = "https://cdn-icons-png.flaticon.com/128/6811/6811518.png"

card   = "#1e293b"
text   = "#f1f5f9"
sub    = "#94a3b8"
border = "#334155"
muted  = "#162032"
green  = "#16a34a"
blue   = "#3b82f6"
amber  = "#f59e0b"
red    = "#dc2626"


def render():
    st.markdown(f"""
    <div style='margin-bottom:24px;display:flex;align-items:center;gap:10px;'>
        <img src='{ABOUT_ICON}' style='width:24px;height:24px;object-fit:contain;filter:brightness(0) invert(1);'>
        <div>
            <h2 style='font-size:20px;font-weight:800;color:{text};margin:0 0 2px 0;'>About NetConfirm</h2>
            <p style='font-size:13px;color:{sub};margin:0;'>A hybrid AI system built to fight misinformation at scale.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero section
    st.markdown(f"""
    <div style='background:{card};border:1px solid {border};border-radius:16px;padding:32px;margin-bottom:20px;
        display:flex;align-items:center;gap:24px;flex-wrap:wrap;'>
        <img src='https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=120&h=120&fit=crop&crop=face'
            style='width:90px;height:90px;border-radius:50%;object-fit:cover;border:3px solid {border};flex-shrink:0;'>
        <div style='flex:1;min-width:200px;'>
            <p style='font-size:18px;font-weight:800;color:{text};margin:0 0 6px 0;'>Hi, I am Taiwo Emmanuel</p>
            <p style='font-size:14px;color:{sub};margin:0;line-height:1.7;'>
                I built NetConfirm as my final year project at Westland University. The internet is full of misleading
                stories and I wanted to build something that actually helps people tell the difference between
                real journalism and misinformation. This is that tool.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # What it does
    st.markdown(f"""
    <div style='background:{muted};border:1px solid {border};border-radius:14px;padding:24px;margin-bottom:20px;'>
        <p style='font-size:15px;font-weight:800;color:{text};margin:0 0 14px 0;'>What NetConfirm Does</p>
        <p style='font-size:14px;color:{sub};margin:0 0 12px 0;line-height:1.8;'>
            NetConfirm analyses news articles using a combination of deep language understanding and social context signals.
            You paste an article or drop a URL and within seconds you get a verdict with a confidence score,
            a full signal breakdown, and an explanation of exactly which words and features drove the decision.
        </p>
        <p style='font-size:14px;color:{sub};margin:0;line-height:1.8;'>
            It supports over 100 languages through automatic translation, works on both individual articles and
            bulk URL batches, and exposes everything through a free REST API so developers can integrate it
            directly into their own apps and workflows.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # How it works
    st.markdown(f"""
    <div style='background:{card};border:1px solid {border};border-radius:14px;padding:24px;margin-bottom:20px;'>
        <p style='font-size:15px;font-weight:800;color:{text};margin:0 0 16px 0;'>How the AI Works</p>
        <div style='display:flex;flex-direction:column;gap:16px;'>
            <div style='display:flex;gap:14px;align-items:flex-start;'>
                <div style='background:{blue}22;border-radius:8px;padding:8px;flex-shrink:0;'>
                    <img src='https://cdn-icons-png.flaticon.com/128/10496/10496548.png'
                        style='width:20px;height:20px;object-fit:contain;filter:brightness(0) invert(1);display:block;'>
                </div>
                <div>
                    <p style='font-size:13px;font-weight:700;color:{text};margin:0 0 4px 0;'>Text Stream — DistilBERT</p>
                    <p style='font-size:13px;color:{sub};margin:0;line-height:1.6;'>
                        The article text is encoded using DistilBERT, a transformer model that understands deep semantic
                        meaning, writing style, and linguistic patterns. It produces a 768-dimensional representation
                        of the content.
                    </p>
                </div>
            </div>
            <div style='display:flex;gap:14px;align-items:flex-start;'>
                <div style='background:{amber}22;border-radius:8px;padding:8px;flex-shrink:0;'>
                    <img src='https://cdn-icons-png.flaticon.com/128/8915/8915911.png'
                        style='width:20px;height:20px;object-fit:contain;filter:brightness(0) invert(1);display:block;'>
                </div>
                <div>
                    <p style='font-size:13px;font-weight:700;color:{text};margin:0 0 4px 0;'>Metadata Stream — Social Context</p>
                    <p style='font-size:13px;color:{sub};margin:0;line-height:1.6;'>
                        Five structured signals capture how and where the article was published: source trust score,
                        author follower count, account age, sentiment polarity, and readability score.
                        Fake news consistently exploits these vectors.
                    </p>
                </div>
            </div>
            <div style='display:flex;gap:14px;align-items:flex-start;'>
                <div style='background:{green}22;border-radius:8px;padding:8px;flex-shrink:0;'>
                    <img src='https://cdn-icons-png.flaticon.com/128/8267/8267389.png'
                        style='width:20px;height:20px;object-fit:contain;filter:brightness(0) invert(1);display:block;'>
                </div>
                <div>
                    <p style='font-size:13px;font-weight:700;color:{text};margin:0 0 4px 0;'>Fusion and Classification</p>
                    <p style='font-size:13px;color:{sub};margin:0;line-height:1.6;'>
                        Both streams are concatenated into a 773-dimensional hybrid vector and classified by an
                        XGBoost ensemble model trained on 72,000 labeled articles from the WELFake benchmark dataset.
                    </p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Performance metrics
    st.markdown(f"""
    <div style='background:{muted};border:1px solid {border};border-radius:14px;padding:24px;margin-bottom:20px;'>
        <p style='font-size:15px;font-weight:800;color:{text};margin:0 0 16px 0;'>Model Performance</p>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    for col, label, val, color in [
        (m1, "Accuracy",     "96.4%",  green),
        (m2, "F1 Score",     "0.963",  blue),
        (m3, "Training Set", "57,600", amber),
        (m4, "Test Set",     "14,400", sub),
    ]:
        col.markdown(f"""
        <div style='background:{card};border:1px solid {border};border-radius:10px;
            padding:16px;text-align:center;'>
            <p style='font-size:11px;color:{sub};margin:0 0 4px 0;
                text-transform:uppercase;letter-spacing:0.5px;'>{label}</p>
            <p style='font-size:24px;font-weight:800;color:{color};margin:0;'>{val}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Interpreting results
    st.markdown(f"""
    <div style='background:{card};border:1px solid {border};border-radius:14px;padding:24px;margin-bottom:20px;'>
        <p style='font-size:15px;font-weight:800;color:{text};margin:0 0 16px 0;'>Reading Your Results</p>
        <div style='display:flex;flex-direction:column;gap:10px;'>
            <div style='display:flex;align-items:center;gap:14px;background:{muted};border-radius:10px;padding:12px 16px;'>
                <div style='width:12px;height:12px;border-radius:50%;background:{green};flex-shrink:0;'></div>
                <div>
                    <span style='font-size:13px;font-weight:700;color:{text};'>75% to 100%</span>
                    <span style='font-size:13px;color:{sub};margin-left:8px;'>Likely authentic with low misinformation risk</span>
                </div>
            </div>
            <div style='display:flex;align-items:center;gap:14px;background:{muted};border-radius:10px;padding:12px 16px;'>
                <div style='width:12px;height:12px;border-radius:50%;background:{amber};flex-shrink:0;'></div>
                <div>
                    <span style='font-size:13px;font-weight:700;color:{text};'>50% to 74%</span>
                    <span style='font-size:13px;color:{sub};margin-left:8px;'>Uncertain — verify with additional sources</span>
                </div>
            </div>
            <div style='display:flex;align-items:center;gap:14px;background:{muted};border-radius:10px;padding:12px 16px;'>
                <div style='width:12px;height:12px;border-radius:50%;background:#f97316;flex-shrink:0;'></div>
                <div>
                    <span style='font-size:13px;font-weight:700;color:{text};'>25% to 49%</span>
                    <span style='font-size:13px;color:{sub};margin-left:8px;'>Likely fake — treat with significant caution</span>
                </div>
            </div>
            <div style='display:flex;align-items:center;gap:14px;background:{muted};border-radius:10px;padding:12px 16px;'>
                <div style='width:12px;height:12px;border-radius:50%;background:{red};flex-shrink:0;'></div>
                <div>
                    <span style='font-size:13px;font-weight:700;color:{text};'>0% to 24%</span>
                    <span style='font-size:13px;color:{sub};margin-left:8px;'>High risk with strong indicators of misinformation</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Trust section with smiling image
    st.markdown(f"""
    <div style='background:{muted};border:1px solid {border};border-radius:14px;padding:24px;margin-bottom:20px;
        display:flex;align-items:center;gap:24px;flex-wrap:wrap;'>
        <img src='https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=120&h=120&fit=crop&crop=face'
            style='width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid {border};flex-shrink:0;'>
        <div style='flex:1;min-width:200px;'>
            <p style='font-size:14px;font-weight:700;color:{text};margin:0 0 6px 0;'>Built for everyone</p>
            <p style='font-size:13px;color:{sub};margin:0;line-height:1.7;'>
                Whether you are a journalist fact-checking a story, a researcher studying misinformation patterns,
                or just someone who wants to know if what they are reading is real, NetConfirm is designed to be
                fast, transparent, and easy to use. No account needed to get started.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Disclaimer
    st.markdown(f"""
    <div style='background:{card};border:1px solid {amber}40;border-left:4px solid {amber};
        border-radius:12px;padding:20px;margin-bottom:20px;'>
        <p style='font-size:13px;font-weight:700;color:{amber};margin:0 0 8px 0;'>Important Disclaimer</p>
        <p style='font-size:13px;color:{sub};margin:0;line-height:1.7;'>
            NetConfirm is a probabilistic analysis tool, not a definitive fact-checker. Results should be treated
            as one signal among many. Always verify important claims with primary sources, credible journalists,
            and established fact-checking organisations such as Africa Check, Snopes, or PolitiFact.
            The system may show reduced accuracy on very recent events or content that differs substantially
            from its training distribution.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
    <p style='font-size:12px;color:{sub};text-align:center;margin-top:8px;'>
        Built by <a href='https://github.com/marvxlab' target='_blank' style='color:{blue};text-decoration:none;display:inline-flex;align-items:center;gap:5px;'><img src='https://cdn-icons-png.flaticon.com/128/733/733553.png' style='width:14px;height:14px;filter:brightness(0) invert(1);'>MarvXLab</a> &nbsp;·&nbsp; Westland University &nbsp;·&nbsp; Computer Science FYP &nbsp;·&nbsp; 2025
    </p>
    """, unsafe_allow_html=True)
