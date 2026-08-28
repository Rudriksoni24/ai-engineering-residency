from dataclasses import dataclass

from rag.generation.generator import LocalGenerator
from rag.generation.prompt_builder import (
    PromptBuilder,
)
from rag.retrieval.retriever import Retriever


@dataclass(frozen=True)
class RAGResponse:
    answer: str
    sources: list[str]
    retrieved_count: int
    retrieved_documents: list[str]
class RAGPipeline:

    def __init__(
        self,
        retriever: Retriever,
        prompt_builder: PromptBuilder,
        generator: LocalGenerator,
    ):
        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.generator = generator

    def answer(
    self,
    query: str,
    top_k: int = 3,
) -> RAGResponse:

        results = self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        if not results:
            return RAGResponse(
                answer=(
                    "I don't know based on the "
                    "provided documents."
                ),
                sources=[],
                retrieved_count=0,
                retrieved_documents=[],
            )

        prompt = self.prompt_builder.build(
            query=query,
            context=results,
        )

        answer = self.generator.generate(
            prompt
        )

        sources = list(
            dict.fromkeys(
                result.source
                for result in results
            )
        )

        retrieved_documents = [
            result.content
            for result in results
        ]

        return RAGResponse(
            answer=answer,
            sources=sources,
            retrieved_count=len(results),
            retrieved_documents=retrieved_documents,
        )