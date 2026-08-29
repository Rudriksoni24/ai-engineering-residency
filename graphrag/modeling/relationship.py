from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Relationship:
    relationship_id: str
    source_id: str
    target_id: str
    relationship_type: str
    properties: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not self.relationship_id.strip():
            raise ValueError(
                "relationship_id cannot be empty"
            )

        if not self.source_id.strip():
            raise ValueError(
                "source_id cannot be empty"
            )

        if not self.target_id.strip():
            raise ValueError(
                "target_id cannot be empty"
            )

        if not self.relationship_type.strip():
            raise ValueError(
                "relationship_type cannot be empty"
            )

        if self.source_id == self.target_id:
            raise ValueError(
                "self relationships are not "
                "allowed in this model"
            )