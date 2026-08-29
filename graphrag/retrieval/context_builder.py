from graphrag.retrieval.contracts import (
    GraphRetrievalResult,
)


class GraphContextBuilder:

    def build(
        self,
        result: GraphRetrievalResult,
    ) -> str:

        if not result.entities:
            return ""

        entities_by_id = {
            item.entity.entity_id:
            item.entity
            for item in result.entities
        }

        lines: list[str] = []

        lines.append(
            "Retrieved graph knowledge:"
        )

        lines.append("")

        lines.append("Entities:")

        for item in result.entities:

            entity = item.entity

            lines.append(
                f"- {entity.name} "
                f"[{entity.entity_type}] "
                f"(id={entity.entity_id}, "
                f"depth={item.depth})"
            )

        if result.relationships:

            lines.append("")
            lines.append(
                "Relationships:"
            )

            for relationship in (
                result.relationships
            ):
                source = entities_by_id[
                    relationship.source_id
                ]

                target = entities_by_id[
                    relationship.target_id
                ]

                lines.append(
                    f"- {source.name} "
                    f"[{source.entity_type}] "
                    f"--["
                    f"{relationship.relationship_type}"
                    f"]--> "
                    f"{target.name} "
                    f"[{target.entity_type}]"
                )

        return "\n".join(lines)