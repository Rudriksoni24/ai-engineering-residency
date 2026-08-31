from typing import Any

from agents.tools.contracts import (
    ToolDefinition,
    ToolParameter,
)


class SearchKnowledgeTool:
    def __init__(
        self,
        *,
        documents: dict[str, dict[str, str]],
    ) -> None:
        self._documents = documents

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_knowledge",
            description=(
                "Search the research knowledge base for documents "
                "relevant to a query."
            ),
            parameters=(
                ToolParameter(
                    name="query",
                    parameter_type="string",
                    description=(
                        "Search terms describing the information needed."
                    ),
                    required=True,
                ),
            ),
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        query = str(
            arguments["query"]
        ).strip()

        query_terms = {
            term.lower()
            for term in query.split()
            if term.strip()
        }

        ranked_results: list[
            tuple[int, str, str]
        ] = []

        for (
            document_id,
            document,
        ) in self._documents.items():
            searchable_text = (
                f"{document['title']} "
                f"{document['content']}"
            ).lower()

            score = sum(
                1
                for term in query_terms
                if term in searchable_text
            )

            if score > 0:
                ranked_results.append(
                    (
                        score,
                        document_id,
                        document["title"],
                    )
                )

        ranked_results.sort(
            key=lambda result: (
                -result[0],
                result[1],
            )
        )

        if not ranked_results:
            return (
                f"No knowledge documents matched query: "
                f"{query}"
            )

        lines = ["Search results:"]

        for (
            _,
            document_id,
            title,
        ) in ranked_results[:5]:
            lines.append(
                f"- {document_id}: {title}"
            )

        return "\n".join(lines)


class ReadDocumentTool:
    def __init__(
        self,
        *,
        documents: dict[str, dict[str, str]],
    ) -> None:
        self._documents = documents

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="read_document",
            description=(
                "Read one research document using its document ID."
            ),
            parameters=(
                ToolParameter(
                    name="document_id",
                    parameter_type="string",
                    description=(
                        "The exact document ID returned by search_knowledge."
                    ),
                    required=True,
                ),
            ),
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> str:
        document_id = str(
            arguments["document_id"]
        ).strip()

        document = self._documents.get(
            document_id
        )

        if document is None:
            return (
                f"Document {document_id} "
                "was not found."
            )

        return (
            f"Document {document_id}: "
            f"{document['title']}\n"
            f"{document['content']}"
        )