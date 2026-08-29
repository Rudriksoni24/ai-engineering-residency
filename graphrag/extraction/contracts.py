from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExtractedEntity:
    name: str
    entity_type: str
    properties: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "entity name cannot be empty"
            )

        if not self.entity_type.strip():
            raise ValueError(
                "entity type cannot be empty"
            )


@dataclass(frozen=True)
class ExtractedRelationship:
    source_name: str
    target_name: str
    relationship_type: str
    properties: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.source_name.strip():
            raise ValueError(
                "source_name cannot be empty"
            )

        if not self.target_name.strip():
            raise ValueError(
                "target_name cannot be empty"
            )

        if not self.relationship_type.strip():
            raise ValueError(
                "relationship_type cannot be empty"
            )


@dataclass(frozen=True)
class KnowledgeExtractionResult:
    entities: list[ExtractedEntity]
    relationships: list[ExtractedRelationship]

    @property
    def entity_count(self) -> int:
        return len(self.entities)

    @property
    def relationship_count(self) -> int:
        return len(self.relationships)