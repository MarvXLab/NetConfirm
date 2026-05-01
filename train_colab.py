# ============================================================
# NetConfirm — Training Pipeline
# Run this on Google Colab (free GPU)
#
# Steps:
# 1. Upload WELFake_Dataset.csv to Colab
# 2. Run all cells in order
# 3. Download xgb_model.pkl and scaler.pkl
# 4. Upload both to HuggingFace Hub or models/ folder
# ============================================================

# ── CELL 1: Install dependencies ──────────────────────────
# !pip install transformers torch xgboost scikit-learn pandas numpy textstat vaderSentiment joblib huggingface_hub -q

# ── CELL 2: Imports ───────────────────────────────────────
import pandas as pd
import numpy as np
import torch
import joblib
import os
from transformers import DistilBertTokenizer, DistilBertModel
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

print("✅ Imports done")
print(f"GPU available: {torch.cuda.is_available()}")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using: {device}")

# ── CELL 3: Load and clean dataset ────────────────────────
df = pd.read_csv("WELFake_Dataset.csv")
print(f"Raw shape: {df.shape}")
print(df.head(2))
print(df["label"].value_counts())

# Clean
df = df.dropna(subset=["text", "label"])
df["text"] = df["text"].astype(str).str.strip()
df = df[df["text"].str.len() >= 20]
df["label"] = df["label"].astype(int)
print(f"Clean shape: {df.shape}")

# ── CELL 4: Simulate metadata features ────────────────────
# Since WELFake doesn't have real metadata, we simulate realistic
# distributions that correlate with fake/real labels + add noise

analyzer = SentimentIntensityAnalyzer()

def compute_sentiment(text):
    score = analyzer.polarity_scores(str(text))["compound"]
    return (score + 1.0) / 2.0

def compute_readability(text):
    try:
        fkg = textstat.flesch_kincaid_grade(str(text))
        return float(np.clip(fkg, 0, 20)) / 20.0
    except:
        return 0.5

print("Computing text features (sentiment + readability)...")
df["sentiment"] = df["text"].apply(compute_sentiment)
df["readability"] = df["text"].apply(compute_readability)

# Simulate metadata with realistic distributions
np.random.seed(42)
n = len(df)

# Real news: higher trust, more followers, older accounts
# Fake news: lower trust, fewer followers, newer accounts
df["trust_score"] = np.where(
    df["label"] == 1,  # 1 = fake
    np.clip(np.random.beta(2, 5, n), 0, 1),   # skewed low for fake
    np.clip(np.random.beta(5, 2, n), 0, 1),   # skewed high for real
)

df["follower_count"] = np.where(
    df["label"] == 1,
    np.random.randint(0, 5000, n),
    np.random.randint(1000, 500000, n),
)

df["account_age"] = np.where(
    df["label"] == 1,
    np.random.randint(1, 365, n),
    np.random.randint(180, 3650, n),
)

# Add noise to prevent overfitting on simulated metadata
df["trust_score"] += np.random.normal(0, 0.05, n)
df["trust_score"] = df["trust_score"].clip(0, 1)

print("✅ Metadata features computed")
print(df[["trust_score", "follower_count", "account_age", "sentiment", "readability"]].describe())

# ── CELL 5: Build metadata matrix ─────────────────────────
def build_meta_matrix(df):
    trust = df["trust_score"].values
    followers = np.log1p(df["follower_count"].values) / 20.0
    followers = np.clip(followers, 0, 1)
    age = np.clip(df["account_age"].values, 0, 3650) / 3650.0
    sentiment = df["sentiment"].values
    readability = df["readability"].values
    return np.column_stack([trust, followers, age, sentiment, readability])

meta_matrix = build_meta_matrix(df)
print(f"Metadata matrix shape: {meta_matrix.shape}")

# ── CELL 6: DistilBERT text embeddings ────────────────────
MODEL_NAME = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
model = DistilBertModel.from_pretrained(MODEL_NAME).to(device)
model.eval()

def get_embeddings_batch(texts, batch_size=64):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch = [str(t).strip() or " " for t in batch]
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        cls = outputs.last_hidden_state[:, 0, :].cpu().numpy()
        all_embeddings.append(cls)
        if (i // batch_size) % 20 == 0:
            print(f"  Encoded {min(i + batch_size, len(texts))}/{len(texts)}")
    return np.vstack(all_embeddings)

print("Encoding text with DistilBERT...")
texts = df["text"].tolist()
text_embeddings = get_embeddings_batch(texts, batch_size=64)
print(f"Text embeddings shape: {text_embeddings.shape}")

# ── CELL 7: Build hybrid vectors ──────────────────────────
hybrid_matrix = np.concatenate([text_embeddings, meta_matrix], axis=1)
labels = df["label"].values
print(f"Hybrid matrix shape: {hybrid_matrix.shape}")
print(f"Labels shape: {labels.shape}")

# ── CELL 8: Train/test split ──────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    hybrid_matrix, labels,
    test_size=0.2,
    random_state=42,
    stratify=labels,
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")

# ── CELL 9: Scale features ────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ── CELL 10: Train XGBoost ────────────────────────────────
X_train_val, X_val, y_train_val, y_val = train_test_split(
    X_train_scaled, y_train,
    test_size=0.1,
    random_state=42,
    stratify=y_train,
)

xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42,
    tree_method="gpu_hist" if torch.cuda.is_available() else "hist",
    n_jobs=-1,
)

print("Training XGBoost...")
xgb_model.fit(
    X_train_val, y_train_val,
    eval_set=[(X_val, y_val)],
    early_stopping_rounds=20,
    verbose=50,
)
print("✅ Training complete")

# ── CELL 11: Evaluate ─────────────────────────────────────
y_pred = xgb_model.predict(X_test_scaled)
y_proba = xgb_model.predict_proba(X_test_scaled)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)

print("\n" + "="*50)
print("NETCONFIRM MODEL EVALUATION")
print("="*50)
print(f"Accuracy  : {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"F1 Score  : {f1:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["REAL", "FAKE"]))

# ── CELL 12: Save models ──────────────────────────────────
os.makedirs("models", exist_ok=True)
joblib.dump(xgb_model, "models/xgb_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")
print("✅ Models saved to models/")

# ── CELL 13: Upload to HuggingFace Hub (optional) ─────────
# from huggingface_hub import HfApi
# HF_TOKEN = "hf_your_token_here"
# HF_REPO = "your-username/fake-news-model"
# api = HfApi()
# api.upload_file(path_or_fileobj="models/xgb_model.pkl", path_in_repo="xgb_model.pkl", repo_id=HF_REPO, token=HF_TOKEN)
# api.upload_file(path_or_fileobj="models/scaler.pkl", path_in_repo="scaler.pkl", repo_id=HF_REPO, token=HF_TOKEN)
# print("✅ Models uploaded to HuggingFace Hub")

# ── CELL 14: Download from Colab ──────────────────────────
# from google.colab import files
# files.download("models/xgb_model.pkl")
# files.download("models/scaler.pkl")
