from pathlib import Path

from rag.ingestion.normalizer import DocumentNormalizer
from rag.loaders.text_loader import TextLoader


def main():
    path = Path(
        "data/examples/reconciliation_policy.txt"
    )

    loader = TextLoader(path)

    document = loader.load()

    normalizer = DocumentNormalizer()

    normalized = normalizer.normalize(document)

    print("SOURCE:")
    print(normalized.source)

    print("\nMETADATA:")
    print(normalized.metadata)

    print("\nCONTENT:")
    print(normalized.content)


if __name__ == "__main__":
    main()