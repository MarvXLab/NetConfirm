import numpy as np
import streamlit as st
from scipy.sparse import hstack, csr_matrix

_explainer = None


def _get_explainer(model):
    global _explainer
    if _explainer is None:
        import shap
        _explainer = shap.TreeExplainer(model)
    return _explainer


@st.cache_data(show_spinner=False)
def get_shap_explanation(text: str, trust_score: float, follower_count: int, account_age: int):
    """
    Returns top words and feature contributions for a single prediction.
    Returns:
        word_scores   : list of (word, shap_value) sorted by abs impact
        feature_scores: list of (feature_name, shap_value) for dense features
        base_value    : float — model base (expected) value
    """
    import shap
    from ml.predict import _load_models
    from ml.fusion import build_hybrid_vector

    model, scaler, tfidf = _load_models()
    explainer = _get_explainer(model)

    # Build feature vector (same pipeline as predict.py)
    hybrid_vec = build_hybrid_vector(text, trust_score, follower_count, account_age)
    tfidf_width = len(tfidf.vocabulary_)
    dense_part = hybrid_vec[:, tfidf_width:].toarray()
    dense_scaled = scaler.transform(dense_part)
    final_vec = hstack([hybrid_vec[:, :tfidf_width], csr_matrix(dense_scaled)]).toarray()

    # SHAP values — index 1 = FAKE class
    shap_vals = explainer.shap_values(final_vec)
    # TreeExplainer returns array of shape (1, n_features) for binary
    if isinstance(shap_vals, list):
        sv = shap_vals[1][0]   # FAKE class, first (only) sample
    else:
        sv = shap_vals[0]

    base_value = float(explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value)

    # ── Word-level SHAP (TF-IDF features) ──────────────────
    vocab_inv = {v: k for k, v in tfidf.vocabulary_.items()}
    tfidf_shap = sv[:tfidf_width]

    # Only keep words that actually appear in the text
    text_words = set(text.lower().split())
    word_scores = []
    for idx, val in enumerate(tfidf_shap):
        if abs(val) > 1e-6:
            word = vocab_inv.get(idx, "")
            if word and word in text_words:
                word_scores.append((word, float(val)))

    word_scores.sort(key=lambda x: abs(x[1]), reverse=True)
    word_scores = word_scores[:20]

    # ── Dense feature SHAP ──────────────────────────────────
    dense_shap = sv[tfidf_width:]
    dense_names = [
        "Sentiment", "Readability", "Text Length", "Word Count",
        "Sentence Count", "Avg Word Length", "Exclamation Ratio",
        "Question Ratio", "Caps Ratio", "Punctuation Ratio",
        "Lexical Diversity", "Clickbait Words",
        "Source Trust", "Follower Count", "Account Age",
    ]
    feature_scores = [(dense_names[i], float(dense_shap[i])) for i in range(min(len(dense_names), len(dense_shap)))]
    feature_scores.sort(key=lambda x: abs(x[1]), reverse=True)

    return word_scores, feature_scores, base_value
