import re

from rag.contracts.document import Document


class DocumentNormalizer:

    def normalize(
        self,
        document: Document,
    ) -> Document:

        content = document.content.strip()

        content = re.sub(
            r"\s+",
            " ",
            content,
        )

        if not content:
            raise ValueError(
                "Document content cannot be empty"
            )

        return Document(
            content=content,
            source=document.source,
            metadata=document.metadata,
        )