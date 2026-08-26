from rag.embeddings.config import EmbeddingConfig
from rag.embeddings.embedder import LocalEmbedder


class FakeModel:

    def encode(
        self,
        values,
        normalize_embeddings=True,
    ):
        if isinstance(values, str):
            return FakeVector(
                [0.1, 0.2]
            )

        return [
            FakeVector(
                [float(index), 0.5]
            )
            for index, _ in enumerate(values)
        ]


class FakeVector:

    def __init__(
        self,
        values,
    ):
        self.values = values

    def tolist(self):
        return self.values


def test_embed_empty_chunks():
    embedder = LocalEmbedder(
        config=EmbeddingConfig(),
        model=FakeModel(),
    )

    result = embedder.embed_chunks([])

    assert result == []