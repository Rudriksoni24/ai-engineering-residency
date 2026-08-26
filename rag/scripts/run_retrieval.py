from pathlib import Path

from rag.chunking.chunker import FixedSizeChunker
from rag.chunking.config import ChunkConfig
from rag.embeddings.config import EmbeddingConfig
from rag.embeddings.embedder import LocalEmbedder
from rag.ingestion.normalizer import DocumentNormalizer
from rag.loaders.text_loader import TextLoader
from rag.retrieval.retriever import Retriever
from rag.retrieval.vector_store import (
    InMemoryVectorStore,
)


def main():
    path = Path(
        "data/examples/reconciliation_policy.txt"
    )

    document = TextLoader(path).load()

    normalized = (
        DocumentNormalizer()
        .normalize(document)
    )

    chunks = (
        FixedSizeChunker(
            ChunkConfig(
                chunk_size=100,
                chunk_overlap=20,
            )
        )
        .chunk(normalized)
    )

    embedder = LocalEmbedder(
        EmbeddingConfig()
    )

    embedded_chunks = (
        embedder.embed_chunks(chunks)
    )

    vector_store = InMemoryVectorStore()

    vector_store.add_embedded_chunks(
        embedded_chunks
    )

    retriever = Retriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    query = (
        "Does every mismatch indicate fraud?"
    )

    results = retriever.retrieve(
        query,
        top_k=3,
    )

    print("\nQUERY:")
    print(query)

    print("\nRESULTS:")

    for result in results:
        print("\n" + "=" * 60)

        print(f"SCORE: {result.score:.4f}")
        print(f"SOURCE: {result.source}")
        print(f"ID: {result.id[:12]}")

        print("\nCONTENT:")
        print(result.content)


if __name__ == "__main__":
    main()

    # uv run --project rag python -m rag.scripts.run_retrieval
