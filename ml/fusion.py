import numpy as np
from scipy.sparse import hstack, csr_matrix
from ml.text_encoder import compute_stat_features, get_text_embedding
from ml.metadata_encoder import build_metadata_vector


def build_hybrid_vector(text: str, trust_score: float, follower_count: int, account_age: int):
    """
    Build the full hybrid feature vector for inference.
    Combines: TF-IDF (sparse) + statistical features + metadata features
    Returns a scipy sparse matrix row (1, n_features)
    """
    # TF-IDF sparse vector
    tfidf_vec = get_text_embedding(text)  # shape (1, tfidf_features) sparse

    # Statistical features (12 dims)
    stat_vec = compute_stat_features(text)  # shape (12,)

    # Metadata features (3 dims: trust, followers_scaled, age_scaled)
    meta_vec = build_metadata_vector(
        trust_score=trust_score,
        follower_count=follower_count,
        account_age=account_age,
        text=text,
    )
    # Only use first 3 metadata features (trust, followers, age) — stat features cover sentiment+readability
    meta_vec_3 = meta_vec[:3]

    # Combine dense features
    dense = np.concatenate([stat_vec, meta_vec_3]).reshape(1, -1)  # shape (1, 15)
    dense_sparse = csr_matrix(dense)

    # Stack sparse + dense
    return hstack([tfidf_vec, dense_sparse])  # shape (1, tfidf_features + 15)
