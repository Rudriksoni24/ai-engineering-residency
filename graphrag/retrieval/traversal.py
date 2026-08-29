from collections import deque

from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import (
    Relationship,
)
from graphrag.retrieval.contracts import (
    GraphTraversalResult,
    TraversedEntity,
)
from graphrag.storage.query_service import (
    GraphQueryService,
)


class GraphTraversal:

    def __init__(
        self,
        query_service: GraphQueryService,
    ) -> None:
        self.query_service = query_service

    def traverse(
        self,
        seed: Entity,
        max_depth: int = 2,
        max_entities: int = 20,
    ) -> GraphTraversalResult:

        if max_depth < 0:
            raise ValueError(
                "max_depth cannot be negative"
            )

        if max_entities < 1:
            raise ValueError(
                "max_entities must be at least 1"
            )

        queue = deque(
            [(seed.entity_id, 0)]
        )

        visited: set[str] = set()

        entities: list[
            TraversedEntity
        ] = []

        relationships_by_id: dict[
            str,
            Relationship,
        ] = {}

        while (
            queue
            and len(entities)
            < max_entities
        ):
            (
                entity_id,
                depth,
            ) = queue.popleft()

            if entity_id in visited:
                continue

            entity = (
                self.query_service
                .find_entity(entity_id)
            )

            if entity is None:
                continue

            visited.add(entity_id)

            entities.append(
                TraversedEntity(
                    entity=entity,
                    depth=depth,
                )
            )

            if depth >= max_depth:
                continue

            outgoing = (
                self.query_service
                .outgoing_relationships(
                    entity_id
                )
            )

            incoming = (
                self.query_service
                .incoming_relationships(
                    entity_id
                )
            )

            relationships = (
                outgoing + incoming
            )

            relationships.sort(
                key=lambda relationship: (
                    relationship
                    .relationship_id
                )
            )

            for relationship in (
                relationships
            ):
                relationships_by_id[
                    relationship
                    .relationship_id
                ] = relationship

                if (
                    relationship.source_id
                    == entity_id
                ):
                    neighbor_id = (
                        relationship.target_id
                    )
                else:
                    neighbor_id = (
                        relationship.source_id
                    )

                if neighbor_id not in visited:
                    queue.append(
                        (
                            neighbor_id,
                            depth + 1,
                        )
                    )

        retrieved_entity_ids = {
            item.entity.entity_id
            for item in entities
        }

        relationships = [
            relationship
            for relationship
            in relationships_by_id.values()
            if (
                relationship.source_id
                in retrieved_entity_ids
                and relationship.target_id
                in retrieved_entity_ids
            )
        ]

        relationships.sort(
            key=lambda relationship: (
                relationship.relationship_id
            )
        )

        return GraphTraversalResult(
            seed_entity=seed,
            entities=entities,
            relationships=relationships,
        )