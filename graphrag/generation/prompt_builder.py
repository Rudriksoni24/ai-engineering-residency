class GraphRAGPromptBuilder:

    def build(
        self,
        query: str,
        graph_context: str,
    ) -> str:

        query = query.strip()
        graph_context = (
            graph_context.strip()
        )

        if not query:
            raise ValueError(
                "query cannot be empty"
            )

        if not graph_context:
            raise ValueError(
                "graph_context cannot be empty"
            )

        return f"""You are a banking knowledge assistant.

Answer the user's question using only the graph knowledge provided below.

Rules:
1. Use only facts supported by the graph knowledge.
2. Preserve the meaning of entity relationships.
3. Do not invent entities, relationships, transactions, accounts, or rules.
4. If the graph knowledge is insufficient, say that you do not know based on the available graph knowledge.
5. Keep the answer concise and factual.

Graph knowledge:
{graph_context}

User question:
{query}

Answer:
"""