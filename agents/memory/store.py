from collections import deque

from agents.memory.contracts import (
    MemoryMessage,
    MemoryRole,
)


class AgentMemory:
    def __init__(
        self,
        max_messages: int = 10,
    ) -> None:
        if max_messages <= 0:
            raise ValueError(
                "max_messages must be greater than zero"
            )

        self._max_messages = max_messages

        self._messages: deque[
            MemoryMessage
        ] = deque(
            maxlen=max_messages
        )

    @property
    def max_messages(self) -> int:
        return self._max_messages

    def remember(
        self,
        *,
        role: MemoryRole,
        content: str,
    ) -> None:
        normalized_content = content.strip()

        if not normalized_content:
            raise ValueError(
                "memory content cannot be empty"
            )

        self._messages.append(
            MemoryMessage(
                role=role,
                content=normalized_content,
            )
        )

    def remember_user(
        self,
        content: str,
    ) -> None:
        self.remember(
            role="user",
            content=content,
        )

    def remember_assistant(
        self,
        content: str,
    ) -> None:
        self.remember(
            role="assistant",
            content=content,
        )

    def messages(
        self,
    ) -> tuple[MemoryMessage, ...]:
        return tuple(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)