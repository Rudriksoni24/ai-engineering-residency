from rag.chunking.chunker import FixedSizeChunker
from rag.chunking.config import ChunkConfig
from rag.contracts.document import Document


def test_chunks_document():
    document = Document(
        content="abcdefghij" * 10,
        source="test.txt",
        metadata={
            "type": "test",
        },
    )

    chunker = FixedSizeChunker(
        ChunkConfig(
            chunk_size=20,
            chunk_overlap=5,
        )
    )

    chunks = chunker.chunk(document)

    assert len(chunks) > 1

    assert chunks[0].content == (
        "abcdefghijabcdefghij"
    )


def test_preserves_metadata():
    document = Document(
        content="hello world",
        source="test.txt",
        metadata={
            "category": "banking",
        },
    )

    chunker = FixedSizeChunker(
        ChunkConfig(
            chunk_size=5,
            chunk_overlap=0,
        )
    )

    chunks = chunker.chunk(document)

    assert chunks[0].metadata["category"] == "banking"


def test_chunk_ids_are_unique():
    document = Document(
        content="abcdefghij" * 5,
        source="test.txt",
    )

    chunker = FixedSizeChunker(
        ChunkConfig(
            chunk_size=10,
            chunk_overlap=0,
        )
    )

    chunks = chunker.chunk(document)

    ids = [
        chunk.id
        for chunk in chunks
    ]

    assert len(ids) == len(set(ids))