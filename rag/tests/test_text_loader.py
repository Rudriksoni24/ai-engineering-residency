from pathlib import Path

import pytest

from rag.loaders.text_loader import TextLoader


def test_load_text_document(
    tmp_path: Path,
):
    file_path = tmp_path / "test.txt"

    file_path.write_text(
        "Hello RAG",
        encoding="utf-8",
    )

    loader = TextLoader(file_path)

    document = loader.load()

    assert document.content == "Hello RAG"
    assert document.metadata["filename"] == "test.txt"


def test_missing_document():
    loader = TextLoader(
        Path("/does/not/exist.txt")
    )

    with pytest.raises(FileNotFoundError):
        loader.load()