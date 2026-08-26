from pathlib import Path

from rag.chunking.chunker import FixedSizeChunker
from rag.chunking.config import ChunkConfig
from rag.embeddings.config import EmbeddingConfig
from rag.embeddings.embedder import LocalEmbedder
from rag.ingestion.normalizer import DocumentNormalizer
from rag.loaders.text_loader import TextLoader


def main():
    path = Path(
        "data/examples/reconciliation_policy.txt"
    )

    document = TextLoader(
        path
    ).load()

    document = (
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
        .chunk(document)
    )

    embedder = LocalEmbedder(
        EmbeddingConfig()
    )

    embedded_chunks = (
        embedder.embed_chunks(chunks)
    )

    print(
        f"Total chunks: {len(embedded_chunks)}"
    )

    for item in embedded_chunks:
        print("\n" + "=" * 60)
        print(f"Chunk ID: {item.chunk_id[:12]}")
        print(
            f"Embedding dimension: "
            f"{len(item.embedding)}"
        )
        print(
            f"Embedding sample: "
            f"{item.embedding[:5]}"
        )
        print(f"Content: {item.content}")

if __name__ == "__main__":
    main()

    # uv run --project rag python -m rag.scripts.run_embeddings