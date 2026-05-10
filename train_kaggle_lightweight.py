# ============================================================
# NetConfirm — Lightweight Training Pipeline
# Run this on Kaggle (no GPU needed, ~5 minutes)
#
# Steps:
# 1. Upload WELFake_Dataset.csv to Kaggle dataset
# 2. Create new Kaggle notebook, add dataset
# 3. Run all cells in order
# 4. Download tfidf_model.pkl, xgb_model.pkl, scaler.pkl
# 5. Upload all 3 to HuggingFace repo
# ============================================================

# ── CELL 1: Install ────────────────────────────────────────
# !pip install xgboost scikit-learn pandas numpy textstat vaderSentiment joblib -q

# ── CELL 2: Imports ───────────────────────────────────────
import pandas as pd
import numpy as np
import joblib
import os
import re
import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
from xgboost import XGBClassifier
from scipy.sparse import hstack, csr_matrix

print("✅ Imports done")

# ── CELL 3: Load dataset ──────────────────────────────────
df = pd.read_csv("/kaggle/input/welfake-dataset/WELFake_Dataset.csv")
df = df.dropna(subset=["text", "label"])
df["text"] = df["text"].astype(str).str.strip()
df = df[df["text"].str.len() >= 20]
df["label"] = df["label"].astype(int)
print(f"✅ Loaded: {df.shape}")

# ── CELL 4: Statistical features ─────────────────────────
analyzer = SentimentIntensityAnalyzer()

def compute_features(text):
    t = str(text)
    words = t.split()
    sentences = re.split(r'[.!?]+', t)
    sentences = [s for s in sentences if s.strip()]

    sentiment = (analyzer.polarity_scores(t)["compound"] + 1.0) / 2.0

    try:
        fkg = float(np.clip(textstat.flesch_kincaid_grade(t), 0, 20)) / 20.0
    except Exception:
        fkg = 0.5

    return [
        sentiment,                                                    # 0 sentiment polarity
        fkg,                                                          # 1 readability
        len(t),                                                       # 2 text length
        len(words),                                                   # 3 word count
        len(sentences) if sentences else 1,                           # 4 sentence count
        np.mean([len(w) for w in words]) if words else 0,            # 5 avg word length
        t.count("!") / max(len(t), 1),                               # 6 exclamation ratio
        t.count("?") / max(len(t), 1),                               # 7 question ratio
        sum(1 for c in t if c.isupper()) / max(len(t), 1),           # 8 caps ratio
        len(re.findall(r'[^\w\s]', t)) / max(len(t), 1),             # 9 punctuation ratio
        len(set(words)) / max(len(words), 1),                        # 10 lexical diversity
        t.count("BREAKING") + t.count("EXCLUSIVE") + t.count("SHOCKING"),  # 11 clickbait words
    ]

print("Computing statistical features...")
stat_features = np.array([compute_features(t) for t in df["text"]])
print(f"✅ Statistical features: {stat_features.shape}")

# ── CELL 5: Simulate metadata ─────────────────────────────
np.random.seed(42)
n = len(df)

df["trust_score"] = np.where(
    df["label"] == 1,
    np.clip(np.random.beta(2, 5, n) + np.random.normal(0, 0.05, n), 0, 1),
    np.clip(np.random.beta(5, 2, n) + np.random.normal(0, 0.05, n), 0, 1)
)
df["follower_count"] = np.where(
    df["label"] == 1,
    np.random.randint(0, 5000, n),
    np.random.randint(1000, 500000, n)
)
df["account_age"] = np.where(
    df["label"] == 1,
    np.random.randint(1, 365, n),
    np.random.randint(180, 3650, n)
)

followers_scaled = np.clip(np.log1p(df["follower_count"].values) / 20.0, 0, 1)
age_scaled = np.clip(df["account_age"].values, 0, 3650) / 3650.0

meta_features = np.column_stack([
    df["trust_score"].values,
    followers_scaled,
    age_scaled,
])
print(f"✅ Metadata features: {meta_features.shape}")

# ── CELL 6: TF-IDF ────────────────────────────────────────
print("Fitting TF-IDF...")
tfidf = TfidfVectorizer(
    max_features=8000,
    ngram_range=(1, 2),
    min_df=3,
    max_df=0.95,
    sublinear_tf=True,
    strip_accents="unicode",
    analyzer="word",
    token_pattern=r"\b[a-zA-Z]{2,}\b",
)
tfidf_matrix = tfidf.fit_transform(df["text"])
print(f"✅ TF-IDF matrix: {tfidf_matrix.shape}")

# ── CELL 7: Combine all features ──────────────────────────
dense_features = np.hstack([stat_features, meta_features])
dense_sparse = csr_matrix(dense_features)
X = hstack([tfidf_matrix, dense_sparse])
y = df["label"].values
print(f"✅ Combined feature matrix: {X.shape}")

# ── CELL 8: Train/test split ──────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"✅ Train: {X_train.shape}, Test: {X_test.shape}")

# ── CELL 9: Scale dense part only ─────────────────────────
# We scale the dense features separately then rebuild
X_train_dense = X_train[:, -dense_features.shape[1]:].toarray()
X_test_dense  = X_test[:, -dense_features.shape[1]:].toarray()

scaler = StandardScaler()
X_train_dense_scaled = scaler.fit_transform(X_train_dense)
X_test_dense_scaled  = scaler.transform(X_test_dense)

X_train_tfidf = X_train[:, :tfidf_matrix.shape[1]]
X_test_tfidf  = X_test[:, :tfidf_matrix.shape[1]]

X_train_final = hstack([X_train_tfidf, csr_matrix(X_train_dense_scaled)])
X_test_final  = hstack([X_test_tfidf,  csr_matrix(X_test_dense_scaled)])
print("✅ Scaled")

# ── CELL 10: Train XGBoost ────────────────────────────────
X_tr, X_val, y_tr, y_val = train_test_split(
    X_train_final, y_train, test_size=0.1, random_state=42, stratify=y_train
)

xgb_model = XGBClassifier(
    n_estimators=500,
    max_depth=7,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.7,
    min_child_weight=3,
    gamma=0.1,
    eval_metric="logloss",
    random_state=42,
    tree_method="hist",
    n_jobs=-1,
    use_label_encoder=False,
)
print("Training XGBoost...")
xgb_model.fit(
    X_tr, y_tr,
    eval_set=[(X_val, y_val)],
    early_stopping_rounds=30,
    verbose=50,
)
print("✅ Training complete")

# ── CELL 11: Evaluate ─────────────────────────────────────
y_pred = xgb_model.predict(X_test_final)
print(f"\nAccuracy:  {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"F1:        {f1_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=["REAL", "FAKE"]))

# ── CELL 12: Save models ──────────────────────────────────
os.makedirs("/kaggle/working/models", exist_ok=True)
joblib.dump(tfidf,     "/kaggle/working/models/tfidf_model.pkl")
joblib.dump(xgb_model, "/kaggle/working/models/xgb_model.pkl")
joblib.dump(scaler,    "/kaggle/working/models/scaler.pkl")

# Save feature config so inference knows the dimensions
import json
config = {
    "tfidf_features": tfidf_matrix.shape[1],
    "stat_features": stat_features.shape[1],
    "meta_features": meta_features.shape[1],
    "dense_features": dense_features.shape[1],
    "total_features": X.shape[1],
}
with open("/kaggle/working/models/feature_config.json", "w") as f:
    json.dump(config, f, indent=2)

print("✅ Saved to /kaggle/working/models/")
print(f"   tfidf_model.pkl")
print(f"   xgb_model.pkl")
print(f"   scaler.pkl")
print(f"   feature_config.json")
print(f"\nConfig: {config}")

# ── CELL 13: Upload to HuggingFace ────────────────────────
# from huggingface_hub import HfApi
# HF_TOKEN = "your_token"
# HF_REPO  = "marvxlab/netconfirm-fake-news-model"
# api = HfApi()
# for fname in ["tfidf_model.pkl", "xgb_model.pkl", "scaler.pkl", "feature_config.json"]:
#     api.upload_file(
#         path_or_fileobj=f"/kaggle/working/models/{fname}",
#         path_in_repo=fname,
#         repo_id=HF_REPO,
#         token=HF_TOKEN,
#     )
# print("✅ Uploaded to HuggingFace")
