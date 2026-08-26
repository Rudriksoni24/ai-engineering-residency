import math

from rag.embeddings.config import EmbeddingConfig
from rag.embeddings.embedder import LocalEmbedder


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
            strict=True,
        )
    )

    magnitude_a = math.sqrt(
        sum(
            value ** 2
            for value in vector_a
        )
    )

    magnitude_b = math.sqrt(
        sum(
            value ** 2
            for value in vector_b
        )
    )

    return dot_product / (
        magnitude_a * magnitude_b
    )


def main():
    embedder = LocalEmbedder(
        EmbeddingConfig()
    )

    transaction_a = (
        "A payment transaction failed "
        "during processing."
    )

    transaction_b = (
        "The financial payment could not "
        "be processed successfully."
    )

    unrelated = (
        "The weather in Pune is pleasant."
    )

    embedding_a = embedder.embed_text(
        transaction_a
    )

    embedding_b = embedder.embed_text(
        transaction_b
    )

    embedding_c = embedder.embed_text(
        unrelated
    )

    print(
        "Similar transaction texts:",
        cosine_similarity(
            embedding_a,
            embedding_b,
        ),
    )

    print(
        "Unrelated texts:",
        cosine_similarity(
            embedding_a,
            embedding_c,
        ),
    )


if __name__ == "__main__":
    main()

    # uv run --project rag python -m rag.scripts.run_similarity