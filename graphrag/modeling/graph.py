from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import (
    Relationship,
)


class KnowledgeGraph:

    def __init__(self) -> None:
        self._entities: dict[str, Entity] = {}
        self._relationships: dict[
            str,
            Relationship,
        ] = {}

    @property
    def entities(self) -> list[Entity]:
        return list(
            self._entities.values()
        )

    @property
    def relationships(
        self,
    ) -> list[Relationship]:
        return list(
            self._relationships.values()
        )

    def add_entity(
        self,
        entity: Entity,
    ) -> None:
        if entity.entity_id in self._entities:
            raise ValueError(
                f"Entity already exists: "
                f"{entity.entity_id}"
            )

        self._entities[
            entity.entity_id
        ] = entity

    def get_entity(
        self,
        entity_id: str,
    ) -> Entity | None:
        return self._entities.get(
            entity_id
        )

    def add_relationship(
        self,
        relationship: Relationship,
    ) -> None:

        if (
            relationship.relationship_id
            in self._relationships
        ):
            raise ValueError(
                "Relationship already exists: "
                f"{relationship.relationship_id}"
            )

        if (
            relationship.source_id
            not in self._entities
        ):
            raise ValueError(
                "Unknown source entity: "
                f"{relationship.source_id}"
            )

        if (
            relationship.target_id
            not in self._entities
        ):
            raise ValueError(
                "Unknown target entity: "
                f"{relationship.target_id}"
            )

        self._relationships[
            relationship.relationship_id
        ] = relationship

    def neighbors(
        self,
        entity_id: str,
    ) -> list[Entity]:

        neighbor_ids: set[str] = set()

        for relationship in (
            self._relationships.values()
        ):
            if (
                relationship.source_id
                == entity_id
            ):
                neighbor_ids.add(
                    relationship.target_id
                )

            elif (
                relationship.target_id
                == entity_id
            ):
                neighbor_ids.add(
                    relationship.source_id
                )

        return [
            self._entities[neighbor_id]
            for neighbor_id
            in neighbor_ids
        ]

    def outgoing_relationships(
        self,
        entity_id: str,
    ) -> list[Relationship]:

        return [
            relationship
            for relationship
            in self._relationships.values()
            if relationship.source_id
            == entity_id
        ]

    def incoming_relationships(
        self,
        entity_id: str,
    ) -> list[Relationship]:

        return [
            relationship
            for relationship
            in self._relationships.values()
            if relationship.target_id
            == entity_id
        ]