import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.auth import require_api_key, make_api_key
from api.models import (
    PredictRequest, PredictResponse,
    URLRequest, URLResponse,
    BatchURLRequest, BatchResponse, BatchResultItem,
    HealthResponse,
)
from ml.predict import predict, _load_models
from ml.translator import detect_language, translate_to_english, LANGUAGE_NAMES

app = FastAPI(
    title="NetConfirm API",
    description="""
## NetConfirm — AI Fake News Detection API

Analyse articles for misinformation using a hybrid XGBoost + TF-IDF model
trained on 72,000+ articles from the WELFake benchmark dataset.

### Authentication
All endpoints (except `/health` and `/keys/register`) require an API key
passed in the `X-API-Key` header.

### Get a Free API Key
Call `POST /keys/register` with just your email — no account needed.

### Model Performance
- **Accuracy:** 96.4%
- **F1 Score:** 0.963
    """,
    version="1.0.0",
    contact={"name": "NetConfirm", "url": "https://github.com/MarvXLab/NetConfirm"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _scrape(url: str):
    try:
        from newspaper import Article
        a = Article(url, request_timeout=10)
        a.download()
        a.parse()
        if not a.text or len(a.text.strip()) < 50:
            return None, "Could not extract article text from this URL."
        return {"text": a.text, "title": a.title or "", "source_url": url}, None
    except Exception as e:
        return None, str(e)


# Health
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Check if the API and models are ready."""
    try:
        _load_models()
        loaded = True
    except Exception:
        loaded = False
    return HealthResponse(status="ok", version="1.0.0", models_loaded=loaded)


# Self-service key registration — no master key needed
@app.post("/keys/register", tags=["Keys"],
          summary="Get a free API key — just enter your email")
async def register_key(email: str, name: str = "default"):
    """
    Register for a free API key using just your email address.
    - One key per email — re-registering replaces the old key
    - No master key or account required
    - Use the returned key in the X-API-Key header
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise HTTPException(status_code=422, detail="Invalid email address.")
    from db.queries import register_api_key
    raw, hashed, prefix = make_api_key()
    try:
        register_api_key(email=email, name=name, key_hash=hashed, key_prefix=prefix)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not register key: {e}")
    return {
        "api_key": raw,
        "prefix":  prefix,
        "email":   email,
        "note":    "Store this key securely — it will not be shown again. Pass it in the X-API-Key header.",
    }


# Lookup key info by email (does NOT return the raw key)
@app.get("/keys/lookup", tags=["Keys"],
         summary="Look up your key info by email")
async def lookup_key(email: str):
    """Check if an email has a registered key and see usage stats."""
    from db.queries import get_key_by_email
    record = get_key_by_email(email)
    if not record:
        raise HTTPException(status_code=404, detail="No key found for this email.")
    return {
        "email":      email,
        "name":       record["name"],
        "key_prefix": record["key_prefix"] + "...",
        "active":     record["active"],
        "requests":   record["requests"],
        "created_at": str(record["created_at"]),
        "last_used":  str(record["last_used"]) if record["last_used"] else None,
    }


# Admin key generation (master key required)
@app.post("/keys/generate", tags=["Keys"],
          summary="Admin: generate a key (requires master key)")
async def create_key(
    name: str = "default",
    email: str = "admin@netconfirm.app",
    _key: str = Depends(require_api_key),
):
    """Admin endpoint — generate a key without email verification."""
    from db.queries import register_api_key
    raw, hashed, prefix = make_api_key()
    register_api_key(email=email, name=name, key_hash=hashed, key_prefix=prefix)
    return {
        "api_key": raw,
        "name":    name,
        "note":    "Store this key securely — it will not be shown again.",
    }


# Predict text
@app.post("/predict", response_model=PredictResponse, tags=["Detection"],
          summary="Analyse article text")
async def predict_text(
    body: PredictRequest,
    _key: str = Depends(require_api_key),
):
    """Analyse article text for misinformation. Auto-detects and translates language."""
    lang_code, lang_name = detect_language(body.text)
    text_en, translated  = translate_to_english(body.text, lang_code)
    try:
        result = predict(
            text=text_en,
            trust_score=body.trust_score,
            follower_count=body.follower_count,
            account_age=body.account_age,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return PredictResponse(
        prediction=result["prediction"],
        confidence=round(result["confidence"], 4),
        fake_prob=round(result["fake_prob"], 4),
        real_prob=round(result["real_prob"], 4),
        sentiment=round(result["sentiment"], 4),
        readability=round(result["readability"], 4),
        language=lang_name,
        translated=translated,
        analysed_at=_now(),
    )


# Predict URL
@app.post("/predict/url", response_model=URLResponse, tags=["Detection"],
          summary="Fetch and analyse a URL")
async def predict_url(
    body: URLRequest,
    _key: str = Depends(require_api_key),
):
    """Fetch an article from a URL and analyse it for misinformation."""
    scraped, err = _scrape(body.url)
    if err or not scraped:
        raise HTTPException(status_code=422, detail=err or "Failed to scrape URL")
    lang_code, lang_name = detect_language(scraped["text"])
    text_en, translated  = translate_to_english(scraped["text"], lang_code)
    try:
        result = predict(
            text=text_en,
            trust_score=body.trust_score,
            follower_count=body.follower_count,
            account_age=body.account_age,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return URLResponse(
        prediction=result["prediction"],
        confidence=round(result["confidence"], 4),
        fake_prob=round(result["fake_prob"], 4),
        real_prob=round(result["real_prob"], 4),
        sentiment=round(result["sentiment"], 4),
        readability=round(result["readability"], 4),
        language=lang_name,
        translated=translated,
        analysed_at=_now(),
        title=scraped.get("title", ""),
        source_url=body.url,
    )


# Batch URLs
@app.post("/predict/batch", response_model=BatchResponse, tags=["Detection"],
          summary="Analyse up to 20 URLs at once")
async def predict_batch(
    body: BatchURLRequest,
    _key: str = Depends(require_api_key),
):
    """Fetch and analyse up to 20 URLs in a single request."""
    results = []
    for url in body.urls[:20]:
        scraped, err = _scrape(url)
        if err or not scraped:
            results.append(BatchResultItem(
                url=url, title="", prediction="ERROR",
                confidence=0, fake_prob=0, real_prob=0,
                language="", error=err or "Scrape failed",
            ))
            continue
        try:
            lang_code, lang_name = detect_language(scraped["text"])
            text_en, _           = translate_to_english(scraped["text"], lang_code)
            result = predict(
                text=text_en,
                trust_score=body.trust_score,
                follower_count=body.follower_count,
                account_age=body.account_age,
            )
            results.append(BatchResultItem(
                url=url,
                title=scraped.get("title", "")[:120],
                prediction=result["prediction"],
                confidence=round(result["confidence"], 4),
                fake_prob=round(result["fake_prob"], 4),
                real_prob=round(result["real_prob"], 4),
                language=lang_name,
                error="",
            ))
        except Exception as e:
            results.append(BatchResultItem(
                url=url, title=scraped.get("title", "")[:120],
                prediction="ERROR", confidence=0, fake_prob=0, real_prob=0,
                language="", error=str(e),
            ))
    return BatchResponse(total=len(results), results=results)


# 404 handler
@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found. Visit /docs for the API reference."},
    )
