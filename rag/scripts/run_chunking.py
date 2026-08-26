from pathlib import Path

from rag.chunking.chunker import FixedSizeChunker
from rag.chunking.config import ChunkConfig
from rag.ingestion.normalizer import DocumentNormalizer
from rag.loaders.text_loader import TextLoader


def main():
    path = Path(
        "data/examples/reconciliation_policy.txt"
    )

    document = TextLoader(path).load()

    normalized = (
        DocumentNormalizer()
        .normalize(document)
    )

    chunker = FixedSizeChunker(
        ChunkConfig(
            chunk_size=100,
            chunk_overlap=20,
        )
        # ChunkConfig(
        #     chunk_size=50,
        #     chunk_overlap=10,
        # )
        # ChunkConfig(
        #     chunk_size=150,
        #     chunk_overlap=30,
        # )
        # ChunkConfig(
        #     chunk_size=500,
        #     chunk_overlap=50,
        # )
    )

    chunks = chunker.chunk(
        normalized
    )

    for chunk in chunks:
        print("\n" + "=" * 60)

        print(
            f"CHUNK INDEX: {chunk.index}"
        )

        print(
            f"CHUNK ID: {chunk.id[:12]}"
        )

        print(
            f"METADATA: {chunk.metadata}"
        )

        print("\nCONTENT:")

        print(chunk.content)


if __name__ == "__main__":
    main()