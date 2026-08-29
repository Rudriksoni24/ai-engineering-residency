from dataclasses import dataclass

from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import (
    Relationship,
)


@dataclass(frozen=True)
class TraversedEntity:
    entity: Entity
    depth: int


@dataclass(frozen=True)
class GraphTraversalResult:
    seed_entity: Entity
    entities: list[TraversedEntity]
    relationships: list[Relationship]

    @property
    def entity_count(self) -> int:
        return len(self.entities)

    @property
    def relationship_count(self) -> int:
        return len(self.relationships)


@dataclass(frozen=True)
class GraphRetrievalResult:
    query: str
    seeds: list[Entity]
    entities: list[TraversedEntity]
    relationships: list[Relationship]

    @property
    def entity_count(self) -> int:
        return len(self.entities)

    @property
    def relationship_count(self) -> int:
        return len(self.relationships)