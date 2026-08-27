from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np
from functools import lru_cache
import torch


class EmbeddingModel:
    _instance: Optional["EmbeddingModel"] = None
    _model: Optional[SentenceTransformer] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            self._model.max_seq_length = 512
    
    @property
    def model(self) -> SentenceTransformer:
        return self._model
    
    def encode(self, texts: List[str], batch_size: int = 32, show_progress_bar: bool = False) -> np.ndarray:
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        return self._model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0]


@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel()


def generate_embeddings(texts: List[str], batch_size: int = 32) -> np.ndarray:
    texts = [text.strip() for text in texts if isinstance(text, str) and text.strip()]
    if not texts:
        raise ValueError(
            "No readable text was found, so embeddings could not be generated. "
            "Check that at least one website is accessible."
        )
    model = get_embedding_model()
    return model.encode(texts, batch_size=batch_size, show_progress_bar=True)


def generate_query_embedding(query: str) -> np.ndarray:
    model = get_embedding_model()
    return model.encode_single(query)
