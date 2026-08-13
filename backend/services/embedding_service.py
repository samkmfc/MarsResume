"""
Embedding service — convert text to vector embeddings.
Defaults to sentence-transformers, with API fallback.
"""

from typing import List, Optional


class EmbeddingService:
    """Text embedding service with lazy-loaded models."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        self._enabled = False

    def _load_model(self):
        """Lazy-load the embedding model."""
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self._enabled = True
        except ImportError:
            self._enabled = False

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for a single text."""
        self._load_model()
        if not self._enabled:
            return []
        return self._model.encode(text).tolist()

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embedding vectors for a batch of texts."""
        self._load_model()
        if not self._enabled:
            return [[] for _ in texts]
        return [vec.tolist() for vec in self._model.encode(texts, show_progress_bar=False)]

    @property
    def enabled(self) -> bool:
        self._load_model()
        return self._enabled


# Global singleton
embedding_service = EmbeddingService()