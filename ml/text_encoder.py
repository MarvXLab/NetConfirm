import numpy as np
import re
import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = None
_tfidf = None

def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer

def get_tfidf():
    """Return the loaded TF-IDF vectorizer (loaded by predict.py)."""
    return _tfidf

def set_tfidf(model):
    global _tfidf
    _tfidf = model

def compute_stat_features(text: str) -> np.ndarray:
    """
    Compute 12 statistical text features.
    Must match exactly what was used during training.
    """
    t = str(text).strip()
    words = t.split()
    sentences = re.split(r'[.!?]+', t)
    sentences = [s for s in sentences if s.strip()]
    analyzer = _get_analyzer()

    sentiment = (analyzer.polarity_scores(t)["compound"] + 1.0) / 2.0

    try:
        fkg = float(np.clip(textstat.flesch_kincaid_grade(t), 0, 20)) / 20.0
    except Exception:
        fkg = 0.5

    return np.array([
        sentiment,
        fkg,
        len(t),
        len(words),
        len(sentences) if sentences else 1,
        np.mean([len(w) for w in words]) if words else 0,
        t.count("!") / max(len(t), 1),
        t.count("?") / max(len(t), 1),
        sum(1 for c in t if c.isupper()) / max(len(t), 1),
        len(re.findall(r'[^\w\s]', t)) / max(len(t), 1),
        len(set(words)) / max(len(words), 1),
        float(t.count("BREAKING") + t.count("EXCLUSIVE") + t.count("SHOCKING")),
    ], dtype=np.float32)

def get_text_embedding(text: str) -> np.ndarray:
    """
    Get TF-IDF sparse vector for text.
    Returns dense numpy array.
    """
    tfidf = get_tfidf()
    if tfidf is None:
        raise RuntimeError("TF-IDF model not loaded. Call set_tfidf() first.")
    vec = tfidf.transform([str(text).strip()])
    return vec  # keep sparse — fusion.py handles it
