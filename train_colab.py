import pandas as pd
import numpy as np
import torch
import joblib
import os
import textstat
from transformers import DistilBertTokenizer, DistilBertModel
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from multiprocessing.pool import ThreadPool

print("✅ Imports done")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using: {device}")

df = pd.read_csv("/kaggle/input/fake-news-classification/WELFake_Dataset.csv")
df = df.dropna(subset=["text", "label"])
df["text"] = df["text"].astype(str).str.strip()
df = df[df["text"].str.len() >= 20]
df["label"] = df["label"].astype(int)
print(f"✅ Loaded: {df.shape}")

analyzer = SentimentIntensityAnalyzer()
texts_list = df["text"].tolist()

def compute_sentiment(text):
    return (analyzer.polarity_scores(str(text))["compound"] + 1.0) / 2.0

def compute_readability(text):
    try:
        return float(np.clip(textstat.flesch_kincaid_grade(str(text)), 0, 20)) / 20.0
    except:
        return 0.5

print("Computing sentiment...")
with ThreadPool(4) as pool:
    df["sentiment"] = pool.map(compute_sentiment, texts_list)

print("Computing readability...")
with ThreadPool(4) as pool:
    df["readability"] = pool.map(compute_readability, texts_list)

np.random.seed(42)
n = len(df)

df["trust_score"] = np.where(df["label"] == 1, np.clip(np.random.beta(2, 5, n), 0, 1), np.clip(np.random.beta(5, 2, n), 0, 1))
df["follower_count"] = np.where(df["label"] == 1, np.random.randint(0, 5000, n), np.random.randint(1000, 500000, n))
df["account_age"] = np.where(df["label"] == 1, np.random.randint(1, 365, n), np.random.randint(180, 3650, n))
df["trust_score"] = (df["trust_score"] + np.random.normal(0, 0.05, n)).clip(0, 1)
print("✅ Metadata features done")

def build_meta_matrix(df):
    trust = df["trust_score"].values
    followers = np.clip(np.log1p(df["follower_count"].values) / 20.0, 0, 1)
    age = np.clip(df["account_age"].values, 0, 3650) / 3650.0
    return np.column_stack([trust, followers, age, df["sentiment"].values, df["readability"].values])

meta_matrix = build_meta_matrix(df)
print(f"✅ Meta matrix: {meta_matrix.shape}")

MODEL_NAME = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
bert_model = DistilBertModel.from_pretrained(MODEL_NAME).to(device)
bert_model.eval()

def get_embeddings_batch(texts, batch_size=128):
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = [str(t).strip() or " " for t in texts[i:i+batch_size]]
        inputs = tokenizer(batch, return_tensors="pt", truncation=True, max_length=128, padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = bert_model(**inputs)
        all_embeddings.append(outputs.last_hidden_state[:, 0, :].cpu().numpy())
        if (i // batch_size) % 10 == 0:
            print(f"  Encoded {min(i+batch_size, len(texts))}/{len(texts)}")
    return np.vstack(all_embeddings)

print("Encoding with DistilBERT...")
text_embeddings = get_embeddings_batch(df["text"].tolist())
print(f"✅ Embeddings: {text_embeddings.shape}")

hybrid_matrix = np.concatenate([text_embeddings, meta_matrix], axis=1)
labels = df["label"].values
print(f"✅ Hybrid matrix: {hybrid_matrix.shape}")

X_train, X_test, y_train, y_test = train_test_split(hybrid_matrix, labels, test_size=0.2, random_state=42, stratify=labels)
print(f"✅ Train: {X_train.shape}, Test: {X_test.shape}")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("✅ Scaled")

X_train_val, X_val, y_train_val, y_val = train_test_split(X_train_scaled, y_train, test_size=0.1, random_state=42, stratify=y_train)

xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42,
    tree_method="gpu_hist" if torch.cuda.is_available() else "hist",
    n_jobs=-1,
)
print("Training XGBoost...")
xgb_model.fit(X_train_val, y_train_val, eval_set=[(X_val, y_val)], early_stopping_rounds=20, verbose=50)
print("✅ Training complete")

y_pred = xgb_model.predict(X_test_scaled)
print(f"Accuracy: {accuracy_score(y_test, y_pred)*100:.2f}%")
print(f"F1: {f1_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall: {recall_score(y_test, y_pred):.4f}")
print(classification_report(y_test, y_pred, target_names=["REAL", "FAKE"]))

os.makedirs("/kaggle/working/models", exist_ok=True)
joblib.dump(xgb_model, "/kaggle/working/models/xgb_model.pkl")
joblib.dump(scaler, "/kaggle/working/models/scaler.pkl")
print("✅ Saved — go to Output tab on the right to download xgb_model.pkl and scaler.pkl")
