from rag.retrieval.types import RetrievalResult


class PromptBuilder:

    def build(
        self,
        query: str,
        context: list[RetrievalResult],
    ) -> str:

        context_text = self._build_context(
            context
        )

        return f"""You are a banking knowledge assistant.

Answer the user's question using ONLY the provided context.

Rules:

1. Do not use knowledge outside the context.
2. Do not invent information.
3. If the answer cannot be found in the context,
   say: "I don't know based on the provided documents."
4. Keep the answer concise and factual.
5. Reference the relevant source when possible.

CONTEXT:

{context_text}

QUESTION:

{query}

ANSWER:
"""

    def _build_context(
        self,
        context: list[RetrievalResult],
    ) -> str:

        if not context:
            return "No relevant context was retrieved."

        sections = []

        for index, result in enumerate(
            context,
            start=1,
        ):
            sections.append(
                f"""[Source {index}]
File: {result.source}
Content:
{result.content}"""
            )

        return "\n\n".join(sections)