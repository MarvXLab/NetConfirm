import torch
import numpy as np
from transformers import DistilBertTokenizer, DistilBertModel

MODEL_NAME = "distilbert-base-uncased"

_tokenizer = None
_model = None


def _load_model():
    global _tokenizer, _model
    if _tokenizer is None:
        _tokenizer = DistilBertTokenizer.from_pretrained(MODEL_NAME)
    if _model is None:
        _model = DistilBertModel.from_pretrained(MODEL_NAME)
        _model.eval()
        # Free unused memory
        import gc
        gc.collect()
    return _tokenizer, _model


def get_text_embedding(text: str) -> np.ndarray:
    """
    Encode article text using DistilBERT.
    Returns 768-dim [CLS] token embedding as numpy array.
    """
    tokenizer, model = _load_model()

    # Sanitize input
    text = str(text).strip()
    if not text:
        return np.zeros(768)

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)

    # [CLS] token — shape (1, 768)
    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()
    return cls_embedding.flatten()  # shape (768,)


def get_batch_embeddings(texts: list, batch_size: int = 32) -> np.ndarray:
    """
    Encode a list of texts in batches.
    Returns array of shape (n_samples, 768).
    Used during training only.
    """
    tokenizer, model = _load_model()
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch = [str(t).strip() or " " for t in batch]

        inputs = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        with torch.no_grad():
            outputs = model(**inputs)

        cls = outputs.last_hidden_state[:, 0, :].numpy()
        all_embeddings.append(cls)

        if (i // batch_size) % 10 == 0:
            print(f"  Encoded {min(i + batch_size, len(texts))}/{len(texts)} articles")

    return np.vstack(all_embeddings)
