from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=10000,
                      description="Article text to analyse (20–10,000 characters)")
    trust_score: float = Field(0.5, ge=0.0, le=1.0,
                               description="Source domain credibility (0=untrusted, 1=trusted)")
    follower_count: int = Field(1000, ge=0, le=500_000_000,
                                description="Author follower count")
    account_age: int = Field(365, ge=0, le=36500,
                             description="Author account age in days")
    source_url: Optional[str] = Field(None, description="Optional source URL")

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Breaking news: Scientists discover new treatment for common cold...",
                "trust_score": 0.7,
                "follower_count": 50000,
                "account_age": 1200,
                "source_url": "https://example.com/article",
            }
        }
    }


class PredictResponse(BaseModel):
    prediction:   str   = Field(..., description="FAKE or REAL")
    confidence:   float = Field(..., description="Confidence score 0–1")
    fake_prob:    float = Field(..., description="Probability of being fake")
    real_prob:    float = Field(..., description="Probability of being real")
    sentiment:    float = Field(..., description="Sentiment polarity 0–1")
    readability:  float = Field(..., description="Readability score 0–1")
    language:     str   = Field(..., description="Detected language")
    translated:   bool  = Field(..., description="Whether text was translated to English")
    analysed_at:  str   = Field(..., description="ISO timestamp of analysis")


class URLRequest(BaseModel):
    url: str = Field(..., description="URL of the article to fetch and analyse")
    trust_score: float = Field(0.5, ge=0.0, le=1.0)
    follower_count: int = Field(1000, ge=0)
    account_age: int = Field(365, ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://example.com/news-article",
                "trust_score": 0.6,
                "follower_count": 10000,
                "account_age": 730,
            }
        }
    }


class URLResponse(PredictResponse):
    title: str = Field("", description="Article title if extracted")
    source_url: str = Field("", description="Original URL")


class BatchURLRequest(BaseModel):
    urls: list[str] = Field(..., min_length=1, max_length=20,
                            description="List of URLs to analyse (max 20)")
    trust_score: float = Field(0.5, ge=0.0, le=1.0)
    follower_count: int = Field(1000, ge=0)
    account_age: int = Field(365, ge=0)


class BatchResultItem(BaseModel):
    url:        str
    title:      str
    prediction: str
    confidence: float
    fake_prob:  float
    real_prob:  float
    language:   str
    error:      str


class BatchResponse(BaseModel):
    total:   int
    results: list[BatchResultItem]


class HealthResponse(BaseModel):
    status:  str
    version: str
    models_loaded: bool
