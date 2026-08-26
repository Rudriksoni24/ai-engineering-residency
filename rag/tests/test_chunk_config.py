import pytest

from rag.chunking.config import ChunkConfig


def test_valid_config():
    config = ChunkConfig(
        chunk_size=100,
        chunk_overlap=20,
    )

    assert config.chunk_size == 100
    assert config.chunk_overlap == 20


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        ChunkConfig(
            chunk_size=0,
            chunk_overlap=0,
        )


def test_negative_overlap():
    with pytest.raises(ValueError):
        ChunkConfig(
            chunk_size=100,
            chunk_overlap=-1,
        )


def test_overlap_must_be_smaller_than_chunk():
    with pytest.raises(ValueError):
        ChunkConfig(
            chunk_size=100,
            chunk_overlap=100,
        )