from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    normalize_embeddings: bool = False