import os
import numpy as np
import joblib
import streamlit as st
from huggingface_hub import hf_hub_download
from ml.fusion import build_hybrid_vector
from ml.metadata_encoder import compute_sentiment, compute_readability

_xgb_model = None
_scaler = None


def _get_hf_config():
    """Get HuggingFace config from secrets or env."""
    try:
        token = st.secrets["huggingface"]["token"]
        repo = st.secrets["huggingface"]["repo"]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.getenv("HF_TOKEN", "")
        repo = os.getenv("HF_REPO", "")
    return token, repo


def _load_models():
    """Load XGBoost model and scaler — from HuggingFace Hub or local models/ folder."""
    global _xgb_model, _scaler

    if _xgb_model is not None and _scaler is not None:
        return _xgb_model, _scaler

    local_xgb = os.path.join("models", "xgb_model.pkl")
    local_scaler = os.path.join("models", "scaler.pkl")

    if os.path.exists(local_xgb) and os.path.exists(local_scaler):
        _xgb_model = joblib.load(local_xgb)
        _scaler = joblib.load(local_scaler)
        return _xgb_model, _scaler

    # Try HuggingFace Hub
    token, repo = _get_hf_config()
    if repo:
        try:
            xgb_path = hf_hub_download(repo_id=repo, filename="xgb_model.pkl", token=token or None)
            scaler_path = hf_hub_download(repo_id=repo, filename="scaler.pkl", token=token or None)
            _xgb_model = joblib.load(xgb_path)
            _scaler = joblib.load(scaler_path)
            return _xgb_model, _scaler
        except Exception as e:
            raise RuntimeError(f"Could not load models from HuggingFace Hub: {e}")

    raise RuntimeError("No trained models found. Please train the model first using the Colab notebook.")


def predict(
    text: str,
    trust_score: float,
    follower_count: int,
    account_age: int,
) -> dict:
    """
    Run full inference pipeline on a single article.

    Returns:
        {
            prediction  : 'REAL' or 'FAKE',
            confidence  : float 0-1 (probability of predicted class),
            fake_prob   : float 0-1,
            real_prob   : float 0-1,
            sentiment   : float 0-1,
            readability : float 0-1,
        }
    """
    # Input validation
    text = str(text).strip()
    if len(text) < 20:
        raise ValueError("Article text is too short for reliable analysis (minimum 20 characters)")
    if len(text) > 10000:
        text = text[:10000]

    model, scaler = _load_models()

    # Build hybrid feature vector
    hybrid_vec = build_hybrid_vector(
        text=text,
        trust_score=trust_score,
        follower_count=follower_count,
        account_age=account_age,
    )

    # Scale
    hybrid_scaled = scaler.transform(hybrid_vec.reshape(1, -1))

    # Predict
    proba = model.predict_proba(hybrid_scaled)[0]
    fake_prob = float(proba[1])
    real_prob = float(proba[0])
    prediction = "FAKE" if fake_prob >= 0.5 else "REAL"
    confidence = fake_prob if prediction == "FAKE" else real_prob

    return {
        "prediction": prediction,
        "confidence": round(confidence, 4),
        "fake_prob": round(fake_prob, 4),
        "real_prob": round(real_prob, 4),
        "sentiment": round(compute_sentiment(text), 4),
        "readability": round(compute_readability(text), 4),
    }
