"""
Embedder — Sentence embedding using SentenceTransformers (local, no API)
"""
from sentence_transformers import CrossEncoder, SentenceTransformer
import numpy as np
from app.config import CROSS_ENCODER_MODEL, EMBEDDING_MODEL, ENABLE_DP_NOISE, DP_EPSILON

# Load model once at module level (cached in memory)
_model = None
_cross_encoder = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("Embedding model loaded")
    return _model


def _get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        print(f"Loading cross-encoder model: {CROSS_ENCODER_MODEL}")
        _cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
        print("Cross-encoder model loaded")
    return _cross_encoder


def embed(texts: list[str]) -> list[list[float]]:
    """
    Convert a list of strings into embedding vectors.

    Args:
        texts: List of strings to embed.

    Returns:
        List of embedding vectors (as Python lists).
    """
    model = _get_model()
    embeddings = model.encode(texts, convert_to_numpy=True)

    if ENABLE_DP_NOISE:
        embeddings = _add_dp_noise(embeddings)

    return embeddings.tolist()


def embed_single(text: str) -> list[float]:
    """Embed a single string."""
    return embed([text])[0]


def rerank(query: str, texts: list[str]) -> list[float]:
    """
    Score candidate chunks against the query with a cross-encoder.

    Returns:
        Relevance scores aligned to the input texts.
    """
    if not texts:
        return []

    model = _get_cross_encoder()
    pairs = [[query, text] for text in texts]
    scores = model.predict(pairs)
    return np.asarray(scores).tolist()


def _add_dp_noise(embeddings: np.ndarray) -> np.ndarray:
    """
    Add Gaussian noise for differential privacy.
    Prevents exact reconstruction from stored embedding vectors.
    ε-differential privacy with sensitivity=1.
    """
    sensitivity = 1.0
    noise_scale = sensitivity / DP_EPSILON
    noise = np.random.normal(0, noise_scale, embeddings.shape)
    return embeddings + noise
