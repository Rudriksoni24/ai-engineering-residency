from pathlib import Path

from rag.contracts.document import Document
from rag.loaders.base import BaseLoader


class TextLoader(BaseLoader):

    def __init__(self, path: Path):
        self.path = path

    def load(self) -> Document:
        if not self.path.exists():
            raise FileNotFoundError(
                f"Document not found: {self.path}"
            )

        content = self.path.read_text(
            encoding="utf-8"
        )

        return Document(
            content=content,
            source=str(self.path),
            metadata={
                "filename": self.path.name,
                "extension": self.path.suffix,
            },
        )