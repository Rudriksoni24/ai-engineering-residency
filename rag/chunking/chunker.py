import hashlib

from rag.chunking.chunk import Chunk
from rag.chunking.config import ChunkConfig
from rag.contracts.document import Document


class FixedSizeChunker:

    def __init__(
        self,
        config: ChunkConfig,
    ):
        self.config = config

    def chunk(
        self,
        document: Document,
    ) -> list[Chunk]:

        content = document.content

        chunks = []

        start = 0
        index = 0

        while start < len(content):

            end = start + self.config.chunk_size

            chunk_content = content[start:end]

            chunk_id = self._create_chunk_id(
                source=document.source,
                index=index,
                content=chunk_content,
            )

            chunks.append(
                Chunk(
                    id=chunk_id,
                    content=chunk_content,
                    source=document.source,
                    index=index,
                    metadata=document.metadata.copy(),
                )
            )

            index += 1

            start += (
                self.config.chunk_size
                - self.config.chunk_overlap
            )

        return chunks

    def _create_chunk_id(
        self,
        source: str,
        index: int,
        content: str,
    ) -> str:

        value = (
            f"{source}:{index}:{content}"
        )

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()