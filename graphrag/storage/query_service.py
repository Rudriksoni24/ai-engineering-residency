from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import (
    Relationship,
)
from graphrag.storage.contracts import (
    GraphStore,
)


class GraphQueryService:

    def __init__(
        self,
        store: GraphStore,
    ) -> None:
        self.store = store

    def all_entities(
        self,
    ) -> list[Entity]:

        return self.store.get_entities()

    def find_entity(
        self,
        entity_id: str,
    ) -> Entity | None:

        return self.store.get_entity(
            entity_id
        )

    def find_entities_by_type(
        self,
        entity_type: str,
    ) -> list[Entity]:

        return (
            self.store
            .get_entities_by_type(
                entity_type
            )
        )

    def find_entities_by_name(
        self,
        name: str,
    ) -> list[Entity]:
        
        return (
            self.store
            .find_entities_by_name(name)
        )

    def neighbors(
        self,
        entity_id: str,
    ) -> list[Entity]:

        neighbor_ids: set[str] = set()

        outgoing = (
            self.store
            .get_outgoing_relationships(
                entity_id
            )
        )

        incoming = (
            self.store
            .get_incoming_relationships(
                entity_id
            )
        )

        for relationship in outgoing:
            neighbor_ids.add(
                relationship.target_id
            )

        for relationship in incoming:
            neighbor_ids.add(
                relationship.source_id
            )

        neighbors: list[Entity] = []

        for neighbor_id in sorted(
            neighbor_ids
        ):
            entity = (
                self.store.get_entity(
                    neighbor_id
                )
            )

            if entity is not None:
                neighbors.append(entity)

        return neighbors

    def outgoing_relationships(
        self,
        entity_id: str,
        relationship_type: str
        | None = None,
    ) -> list[Relationship]:

        relationships = (
            self.store
            .get_outgoing_relationships(
                entity_id
            )
        )

        if relationship_type is None:
            return relationships

        return [
            relationship
            for relationship
            in relationships
            if (
                relationship.relationship_type
                == relationship_type
            )
        ]

    def incoming_relationships(
        self,
        entity_id: str,
        relationship_type: str
        | None = None,
    ) -> list[Relationship]:

        relationships = (
            self.store
            .get_incoming_relationships(
                entity_id
            )
        )

        if relationship_type is None:
            return relationships

        return [
            relationship
            for relationship
            in relationships
            if (
                relationship.relationship_type
                == relationship_type
            )
        ]