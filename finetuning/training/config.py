from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LocalLoRAConfig:
    model_name: str = (
        "HuggingFaceTB/SmolLM2-135M-Instruct"
    )

    rank: int = 4
    alpha: int = 8
    dropout: float = 0.05

    target_modules: tuple[str, ...] = (
        "q_proj",
        "v_proj",
    )

    learning_rate: float = 5e-4
    training_steps: int = 20

    max_length: int = 128

    seed: int = 42

    output_dir: Path = Path(
        "artifacts/sprint07/day03-smollm2-lora"
    )

    def validate(self) -> None:
        if not self.model_name.strip():
            raise ValueError(
                "model_name cannot be empty"
            )

        if self.rank <= 0:
            raise ValueError(
                "rank must be greater than zero"
            )

        if self.alpha <= 0:
            raise ValueError(
                "alpha must be greater than zero"
            )

        if not 0.0 <= self.dropout < 1.0:
            raise ValueError(
                "dropout must be in [0.0, 1.0)"
            )

        if not self.target_modules:
            raise ValueError(
                "target_modules cannot be empty"
            )

        if self.learning_rate <= 0:
            raise ValueError(
                "learning_rate must be greater than zero"
            )

        if self.training_steps <= 0:
            raise ValueError(
                "training_steps must be greater than zero"
            )

        if self.max_length <= 0:
            raise ValueError(
                "max_length must be greater than zero"
            )