from sentence_transformers import SentenceTransformer

from rag.chunking.chunk import Chunk
from rag.embeddings.config import EmbeddingConfig
from rag.embeddings.types import EmbeddedChunk


class LocalEmbedder:

    def __init__(
        self,
        config: EmbeddingConfig,
        model=None,
    ):
        self.config = config

        self.model = (
            model
            if model is not None
            else SentenceTransformer(
                config.model_name
            )
        )

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        embedding = self.model.encode(
            text,
            normalize_embeddings=(
                self.config.normalize_embeddings
            ),
        )

        return embedding.tolist()

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[EmbeddedChunk]:

        if not chunks:
            return []

        contents = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = self.model.encode(
            contents,
            normalize_embeddings=(
                self.config.normalize_embeddings
            ),
        )

        return [
            EmbeddedChunk(
                chunk_id=chunk.id,
                content=chunk.content,
                source=chunk.source,
                index=chunk.index,
                embedding=embedding.tolist(),
                model=self.config.model_name,
                metadata=chunk.metadata.copy(),
            )
            for chunk, embedding in zip(
                chunks,
                embeddings,
                strict=True,
            )
        ]