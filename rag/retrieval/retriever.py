from rag.embeddings.embedder import LocalEmbedder
from rag.retrieval.types import RetrievalResult
from rag.retrieval.vector_store import (
    InMemoryVectorStore,
)


class Retriever:

    def __init__(
        self,
        embedder: LocalEmbedder,
        vector_store: InMemoryVectorStore,
    ):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:

        query_embedding = (
            self.embedder.embed_text(query)
        )

        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )