from typing import Protocol

from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import Relationship


class GraphStore(Protocol):

    def add_entity(
        self,
        entity: Entity,
    ) -> None:
        ...

    def get_entity(
        self,
        entity_id: str,
    ) -> Entity | None:
        ...

    def get_entities(
        self,
    ) -> list[Entity]:
        ...

    def get_entities_by_type(
        self,
        entity_type: str,
    ) -> list[Entity]:
        ...

    def add_relationship(
        self,
        relationship: Relationship,
    ) -> None:
        ...

    def get_relationships(
        self,
    ) -> list[Relationship]:
        ...

    def get_outgoing_relationships(
        self,
        entity_id: str,
    ) -> list[Relationship]:
        ...

    def get_incoming_relationships(
        self,
        entity_id: str,
    ) -> list[Relationship]:
        ...