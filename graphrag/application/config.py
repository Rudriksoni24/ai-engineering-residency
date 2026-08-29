from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BankingGraphConfig:
    database_path: Path
    model: str
    max_depth: int = 2
    max_entities: int = 20

    def __post_init__(
        self,
    ) -> None:

        if not self.model.strip():
            raise ValueError(
                "model cannot be empty"
            )

        if self.max_depth < 0:
            raise ValueError(
                "max_depth cannot be negative"
            )

        if self.max_entities < 1:
            raise ValueError(
                "max_entities must be at least 1"
            )