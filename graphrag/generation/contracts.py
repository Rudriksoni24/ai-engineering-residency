from typing import Protocol


class TextGenerator(Protocol):

    def generate(
        self,
        prompt: str,
    ) -> str:
        ...