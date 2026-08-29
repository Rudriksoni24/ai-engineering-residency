from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Entity:
    entity_id: str
    entity_type: str
    name: str
    properties: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.entity_id.strip():
            raise ValueError(
                "entity_id cannot be empty"
            )

        if not self.entity_type.strip():
            raise ValueError(
                "entity_type cannot be empty"
            )

        if not self.name.strip():
            raise ValueError(
                "name cannot be empty"
            )