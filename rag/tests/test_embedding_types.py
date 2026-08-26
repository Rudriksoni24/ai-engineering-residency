from rag.embeddings.types import EmbeddedChunk


def test_embedded_chunk():
    embedded = EmbeddedChunk(
        chunk_id="chunk-1",
        content="Hello",
        source="test-source",
        index=0,
        embedding=[
            0.1,
            0.2,
            0.3,
        ],
        model="test-model",
    )

    assert embedded.chunk_id == "chunk-1"
    assert len(embedded.embedding) == 3
    assert embedded.model == "test-model"