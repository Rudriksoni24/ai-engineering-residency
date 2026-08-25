import pytest

from rag.contracts.document import Document
from rag.ingestion.normalizer import DocumentNormalizer


def test_normalizes_whitespace():
    document = Document(
        content="Hello    world\n\nRAG",
        source="test",
    )

    normalizer = DocumentNormalizer()

    result = normalizer.normalize(document)

    assert result.content == "Hello world RAG"


def test_rejects_empty_document():
    document = Document(
        content="   ",
        source="test",
    )

    normalizer = DocumentNormalizer()

    with pytest.raises(ValueError):
        normalizer.normalize(document)