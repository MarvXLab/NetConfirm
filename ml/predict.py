import os
import numpy as np
import joblib
import streamlit as st
from huggingface_hub import hf_hub_download
from ml.fusion import build_hybrid_vector
from ml.text_encoder import set_tfidf, compute_stat_features
from ml.metadata_encoder import compute_sentiment, compute_readability

_xgb_model = None
_scaler    = None
_tfidf     = None


def _get_hf_config():
    token, repo = "", ""
    # Try st.secrets silently — on Render there is no secrets file so we skip
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            token = st.secrets.get("huggingface", {}).get("token", "")
            repo  = st.secrets.get("huggingface", {}).get("repo", "")
    except Exception:
        pass
    # Always also check env vars so Render environment variables take effect
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    token = token or os.getenv("HF_TOKEN", "")
    repo  = repo  or os.getenv("HF_REPO", "marvxlab/netconfirm-fake-news-model")
    return token, repo


def _load_models():
    global _xgb_model, _scaler, _tfidf

    if _xgb_model is not None and _scaler is not None and _tfidf is not None:
        return _xgb_model, _scaler, _tfidf

    local_xgb   = os.path.join("models", "xgb_model.pkl")
    local_scaler = os.path.join("models", "scaler.pkl")
    local_tfidf  = os.path.join("models", "tfidf_model.pkl")

    if os.path.exists(local_xgb) and os.path.exists(local_scaler) and os.path.exists(local_tfidf):
        _xgb_model = joblib.load(local_xgb)
        _scaler    = joblib.load(local_scaler)
        _tfidf     = joblib.load(local_tfidf)
        set_tfidf(_tfidf)
        return _xgb_model, _scaler, _tfidf

    # Try HuggingFace Hub
    token, repo = _get_hf_config()
    if repo:
        try:
            xgb_path   = hf_hub_download(repo_id=repo, filename="xgb_model.pkl",   token=token or None)
            scaler_path = hf_hub_download(repo_id=repo, filename="scaler.pkl",      token=token or None)
            tfidf_path  = hf_hub_download(repo_id=repo, filename="tfidf_model.pkl", token=token or None)
            _xgb_model = joblib.load(xgb_path)
            _scaler    = joblib.load(scaler_path)
            _tfidf     = joblib.load(tfidf_path)
            set_tfidf(_tfidf)
            return _xgb_model, _scaler, _tfidf
        except Exception as e:
            raise RuntimeError(f"Could not load models from HuggingFace Hub: {e}")

    raise RuntimeError("No trained models found. Please train the model first using train_kaggle_lightweight.py")


def predict(text: str, trust_score: float, follower_count: int, account_age: int) -> dict:
    """
    Run full inference pipeline on a single article.
    Returns prediction, confidence, probabilities and signal scores.
    """
    text = str(text).strip()
    if len(text) < 20:
        raise ValueError("Article text is too short (minimum 20 characters)")
    if len(text) > 10000:
        text = text[:10000]

    model, scaler, tfidf = _load_models()

    # Build hybrid feature vector (sparse)
    hybrid_vec = build_hybrid_vector(
        text=text,
        trust_score=trust_score,
        follower_count=follower_count,
        account_age=account_age,
    )

    # Scale dense part — get tfidf width from the loaded model
    tfidf_width = len(tfidf.vocabulary_)
    dense_part  = hybrid_vec[:, tfidf_width:].toarray()
    dense_scaled = scaler.transform(dense_part)

    from scipy.sparse import hstack, csr_matrix
    final_vec = hstack([hybrid_vec[:, :tfidf_width], csr_matrix(dense_scaled)])

    # Predict
    proba      = model.predict_proba(final_vec)[0]
    fake_prob  = float(proba[1])
    real_prob  = float(proba[0])
    prediction = "FAKE" if fake_prob >= 0.5 else "REAL"
    confidence = fake_prob if prediction == "FAKE" else real_prob

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "fake_prob":  round(fake_prob, 4),
        "real_prob":  round(real_prob, 4),
        "sentiment":  round(compute_sentiment(text), 4),
        "readability": round(compute_readability(text), 4),
    }
