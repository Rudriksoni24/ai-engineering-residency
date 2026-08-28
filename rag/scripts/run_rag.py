from pathlib import Path

from rag.chunking.chunker import FixedSizeChunker
from rag.chunking.config import ChunkConfig
from rag.embeddings.config import EmbeddingConfig
from rag.embeddings.embedder import LocalEmbedder
from rag.generation.generator import LocalGenerator
from rag.generation.prompt_builder import (
    PromptBuilder,
)
from rag.ingestion.normalizer import (
    DocumentNormalizer,
)
from rag.loaders.text_loader import TextLoader
from rag.pipeline.rag_pipeline import RAGPipeline
from rag.retrieval.retriever import Retriever
from rag.retrieval.vector_store import (
    InMemoryVectorStore,
)


def main():
    path = Path(
        "data/examples/reconciliation_policy.txt"
    )

    document = TextLoader(
        path
    ).load()

    document = (
        DocumentNormalizer()
        .normalize(document)
    )

    chunks = (
        FixedSizeChunker(
            ChunkConfig(
                chunk_size=100,
                chunk_overlap=20,
            )
        )
        .chunk(document)
    )

    embedder = LocalEmbedder(
        EmbeddingConfig()
    )

    embedded_chunks = (
        embedder.embed_chunks(chunks)
    )

    vector_store = (
        InMemoryVectorStore()
    )

    vector_store.add_embedded_chunks(
        embedded_chunks
    )

    retriever = Retriever(
        embedder=embedder,
        vector_store=vector_store,
    )

    from local_llm.runtime.ollama_runtime import OllamaRuntime

    llm_client = OllamaRuntime()

    generator = LocalGenerator(
        llm_client=llm_client
    )

    pipeline = RAGPipeline(
        retriever=retriever,
        prompt_builder=PromptBuilder(),
        generator=generator,
    )

    query = (
        "What is the process for investigating inconsistent transactions?"
    )

    response = pipeline.answer(
        query=query,
        top_k=3,
    )

    print("\nQUESTION")
    print(query)

    print("\nANSWER")
    print(response.answer)

    print("\nSOURCES")

    for source in response.sources:
        print(f"- {source}")

    print(
        f"\nRetrieved chunks: "
        f"{response.retrieved_count}"
    )


if __name__ == "__main__":
    main()

    # uv run --project rag python -m rag.scripts.run_rag