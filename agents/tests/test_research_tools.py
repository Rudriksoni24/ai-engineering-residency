from agents.data.research_corpus import (
    RESEARCH_CORPUS,
)
from agents.tools.research import (
    ReadDocumentTool,
    SearchKnowledgeTool,
)


def test_search_knowledge_finds_relevant_document():
    tool = SearchKnowledgeTool(
        documents=RESEARCH_CORPUS
    )

    result = tool.execute(
        {
            "query": "guardrails policy",
        }
    )

    assert "doc-guardrails" in result
    assert "Agent Guardrails" in result


def test_search_knowledge_returns_no_match():
    tool = SearchKnowledgeTool(
        documents=RESEARCH_CORPUS
    )

    result = tool.execute(
        {
            "query": "quantum submarine",
        }
    )

    assert (
        "No knowledge documents matched"
        in result
    )


def test_read_document_returns_content():
    tool = ReadDocumentTool(
        documents=RESEARCH_CORPUS
    )

    result = tool.execute(
        {
            "document_id": (
                "doc-tool-execution"
            )
        }
    )

    assert (
        "Agent Tool Execution"
        in result
    )

    assert (
        "required arguments"
        in result
    )


def test_read_document_handles_unknown_document():
    tool = ReadDocumentTool(
        documents=RESEARCH_CORPUS
    )

    result = tool.execute(
        {
            "document_id": "missing-doc"
        }
    )

    assert result == (
        "Document missing-doc "
        "was not found."
    )


def test_search_tool_definition():
    tool = SearchKnowledgeTool(
        documents=RESEARCH_CORPUS
    )

    definition = tool.definition

    assert (
        definition.name
        == "search_knowledge"
    )

    assert (
        len(definition.parameters)
        == 1
    )

    assert (
        definition.parameters[0].name
        == "query"
    )


def test_read_tool_definition():
    tool = ReadDocumentTool(
        documents=RESEARCH_CORPUS
    )

    definition = tool.definition

    assert (
        definition.name
        == "read_document"
    )

    assert (
        definition.parameters[0].name
        == "document_id"
    )