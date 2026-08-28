from rag.generation.generator import LocalGenerator
from rag.generation.prompt_builder import (
    PromptBuilder,
)
from rag.pipeline.rag_pipeline import RAGPipeline
from rag.retrieval.types import RetrievalResult
from local_llm.runtime.runtime_types import GenerationResponse 


class FakeRetriever:

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[RetrievalResult]:

        return [
            RetrievalResult(
                id="chunk-1",
                content=(
                    "All transaction mismatches "
                    "must be investigated."
                ),
                source="policy.txt",
                score=0.95,
                metadata={},
            )
        ]


class FakeLLM:

    def generate(
        self,
        prompt: str,
    ) -> str:

        return GenerationResponse(
            text="Transaction mismatches must be investigated.",
            model="mock-model",  
            metadata={}
        )


def test_rag_pipeline():
    pipeline = RAGPipeline(
        retriever=FakeRetriever(),
        prompt_builder=PromptBuilder(),
        generator=LocalGenerator(
            llm_client=FakeLLM()
        ),
    )

    response = pipeline.answer(
        "How are mismatches handled?"
    )

    assert (
        response.answer
        == "Transaction mismatches must "
        "be investigated."
    )

    assert response.sources == [
        "policy.txt"
    ]

    assert response.retrieved_count == 1

class EmptyRetriever:

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[RetrievalResult]:

        return []


def test_rag_pipeline_handles_empty_context():
    pipeline = RAGPipeline(
        retriever=EmptyRetriever(),
        prompt_builder=PromptBuilder(),
        generator=LocalGenerator(
            llm_client=FakeLLM()
        ),
    )

    response = pipeline.answer(
        "Unknown question"
    )

    assert response.retrieved_count == 0