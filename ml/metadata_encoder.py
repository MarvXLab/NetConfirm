import numpy as np
import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def compute_sentiment(text: str) -> float:
    """
    VADER compound sentiment score shifted to 0-1 range.
    Original range: -1.0 to 1.0 → shifted to 0.0 to 1.0
    """
    analyzer = _get_analyzer()
    score = analyzer.polarity_scores(str(text))["compound"]
    return (score + 1.0) / 2.0


def compute_readability(text: str) -> float:
    """
    Flesch-Kincaid Grade Level normalized to 0-1.
    Clamped to 0-20 range then scaled.
    Fake news often targets lower reading levels.
    """
    try:
        fkg = textstat.flesch_kincaid_grade(str(text))
        fkg = max(0.0, min(20.0, fkg))
        return fkg / 20.0
    except Exception:
        return 0.5


def build_metadata_vector(
    trust_score: float,
    follower_count: int,
    account_age: int,
    text: str = "",
    sentiment: float = None,
    readability: float = None,
) -> np.ndarray:
    """
    Build the 5-dim metadata feature vector.

    Features:
        0 - source_trust_score  : float 0-1 (already normalized)
        1 - follower_count      : log-transformed then scaled
        2 - account_age_days    : scaled to 0-1 (max assumed 3650 = 10 years)
        3 - sentiment_polarity  : VADER compound shifted to 0-1
        4 - readability_score   : FKG normalized to 0-1
    """
    # Trust score — clamp to 0-1
    trust = float(np.clip(trust_score, 0.0, 1.0))

    # Follower count — log transform then scale (max log ~20 for 500M followers)
    followers = float(follower_count) if follower_count >= 0 else 0.0
    followers_log = np.log1p(followers) / 20.0
    followers_scaled = float(np.clip(followers_log, 0.0, 1.0))

    # Account age — scale to 0-1 (cap at 10 years = 3650 days)
    age = float(np.clip(account_age, 0, 3650)) / 3650.0

    # Sentiment — compute from text if not provided
    if sentiment is None:
        sentiment = compute_sentiment(text) if text else 0.5
    sentiment = float(np.clip(sentiment, 0.0, 1.0))

    # Readability — compute from text if not provided
    if readability is None:
        readability = compute_readability(text) if text else 0.5
    readability = float(np.clip(readability, 0.0, 1.0))

    return np.array([trust, followers_scaled, age, sentiment, readability], dtype=np.float32)


def validate_metadata_inputs(trust_score, follower_count, account_age):
    """Validate user-provided metadata inputs. Returns (is_valid, error_message)."""
    errors = []

    if not (0.0 <= float(trust_score) <= 1.0):
        errors.append("Trust score must be between 0.0 and 1.0")

    if int(follower_count) < 0:
        errors.append("Follower count cannot be negative")

    if int(account_age) < 0:
        errors.append("Account age cannot be negative")

    if int(account_age) > 36500:
        errors.append("Account age seems unrealistic (max 100 years)")

    return len(errors) == 0, errors
