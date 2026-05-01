import numpy as np
from ml.text_encoder import get_text_embedding
from ml.metadata_encoder import build_metadata_vector


def build_hybrid_vector(
    text: str,
    trust_score: float,
    follower_count: int,
    account_age: int,
) -> np.ndarray:
    """
    Build the full 773-dim hybrid feature vector.
    768 (DistilBERT [CLS]) + 5 (metadata) = 773 dims.
    Used at inference time.
    """
    text_vec = get_text_embedding(text)           # shape (768,)
    meta_vec = build_metadata_vector(             # shape (5,)
        trust_score=trust_score,
        follower_count=follower_count,
        account_age=account_age,
        text=text,
    )
    return np.concatenate([text_vec, meta_vec])   # shape (773,)


def build_hybrid_matrix(text_embeddings: np.ndarray, metadata_matrix: np.ndarray) -> np.ndarray:
    """
    Concatenate pre-computed text embeddings and metadata matrix.
    Used during training for efficiency.

    Args:
        text_embeddings : shape (n_samples, 768)
        metadata_matrix : shape (n_samples, 5)
    Returns:
        hybrid_matrix   : shape (n_samples, 773)
    """
    assert text_embeddings.shape[0] == metadata_matrix.shape[0], \
        "Mismatch: text and metadata must have same number of samples"
    return np.concatenate([text_embeddings, metadata_matrix], axis=1)
