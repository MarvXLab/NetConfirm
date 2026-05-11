import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.auth import require_api_key, generate_api_key
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
All endpoints (except `/health`) require an API key passed in the `X-API-Key` header.

### Endpoints
- `POST /predict` — Analyse article text
- `POST /predict/url` — Fetch and analyse a URL
- `POST /predict/batch` — Analyse up to 20 URLs at once
- `GET /health` — Service health check

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


def _scrape(url: str) -> tuple[dict | None, str | None]:
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


# ── Health ────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Check if the API and models are ready."""
    try:
        _load_models()
        loaded = True
    except Exception:
        loaded = False
    return HealthResponse(status="ok", version="1.0.0", models_loaded=loaded)


# ── Predict text ──────────────────────────────────────────
@app.post("/predict", response_model=PredictResponse, tags=["Detection"],
          summary="Analyse article text")
async def predict_text(
    body: PredictRequest,
    _key: str = Depends(require_api_key),
):
    """
    Analyse a piece of article text for misinformation.

    - Automatically detects language and translates to English if needed
    - Returns verdict (FAKE/REAL), confidence, probabilities and signal scores
    """
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


# ── Predict URL ───────────────────────────────────────────
@app.post("/predict/url", response_model=URLResponse, tags=["Detection"],
          summary="Fetch and analyse a URL")
async def predict_url(
    body: URLRequest,
    _key: str = Depends(require_api_key),
):
    """
    Fetch an article from a URL and analyse it for misinformation.

    - Scrapes article text using newspaper3k
    - Auto-detects language and translates if needed
    """
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


# ── Batch URLs ────────────────────────────────────────────
@app.post("/predict/batch", response_model=BatchResponse, tags=["Detection"],
          summary="Analyse up to 20 URLs at once")
async def predict_batch(
    body: BatchURLRequest,
    _key: str = Depends(require_api_key),
):
    """
    Fetch and analyse up to 20 URLs in a single request.

    - Each URL is scraped, language-detected, translated if needed, then analysed
    - Failed URLs are included in results with an error message
    """
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


# ── Dev key generation (protected by master key) ──────────
@app.post("/keys/generate", tags=["Keys"],
          summary="Generate a new API key (requires master key)")
async def create_key(
    name: str = "default",
    _key: str = Depends(require_api_key),
):
    """Generate a new API key. Requires the master key in X-API-Key header."""
    new_key = generate_api_key(name)
    return {
        "api_key": new_key,
        "name": name,
        "note": "Store this key securely — it will not be shown again.",
    }


# ── 404 handler ───────────────────────────────────────────
@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found. Visit /docs for the API reference."},
    )
