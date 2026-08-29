from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import (
    Relationship,
)
from graphrag.retrieval.contracts import (
    GraphRetrievalResult,
    TraversedEntity,
)
from graphrag.retrieval.entity_resolver import (
    EntityResolver,
)
from graphrag.retrieval.traversal import (
    GraphTraversal,
)


class GraphRetriever:

    def __init__(
        self,
        entity_resolver: EntityResolver,
        traversal: GraphTraversal,
    ) -> None:
        self.entity_resolver = (
            entity_resolver
        )
        self.traversal = traversal

    def retrieve(
        self,
        query: str,
        max_depth: int = 2,
        max_entities: int = 20,
    ) -> GraphRetrievalResult:

        seeds = (
            self.entity_resolver
            .resolve(query)
        )

        if not seeds:
            return GraphRetrievalResult(
                query=query,
                seeds=[],
                entities=[],
                relationships=[],
            )

        entities_by_id: dict[
            str,
            TraversedEntity,
        ] = {}

        relationships_by_id: dict[
            str,
            Relationship,
        ] = {}

        for seed in seeds:

            remaining = (
                max_entities
                - len(entities_by_id)
            )

            if remaining <= 0:
                break

            result = (
                self.traversal.traverse(
                    seed=seed,
                    max_depth=max_depth,
                    max_entities=remaining,
                )
            )

            for traversed in (
                result.entities
            ):
                entity_id = (
                    traversed
                    .entity
                    .entity_id
                )

                existing = (
                    entities_by_id.get(
                        entity_id
                    )
                )

                if (
                    existing is None
                    or traversed.depth
                    < existing.depth
                ):
                    entities_by_id[
                        entity_id
                    ] = traversed

            for relationship in (
                result.relationships
            ):
                relationships_by_id[
                    relationship
                    .relationship_id
                ] = relationship

        entity_ids = set(
            entities_by_id
        )

        relationships = [
            relationship
            for relationship
            in relationships_by_id.values()
            if (
                relationship.source_id
                in entity_ids
                and relationship.target_id
                in entity_ids
            )
        ]

        entities = sorted(
            entities_by_id.values(),
            key=lambda item: (
                item.depth,
                item.entity.entity_id,
            ),
        )

        relationships.sort(
            key=lambda relationship: (
                relationship.relationship_id
            )
        )

        return GraphRetrievalResult(
            query=query,
            seeds=seeds,
            entities=entities,
            relationships=relationships,
        )