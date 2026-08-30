import pytest

from agents.memory.store import (
    AgentMemory,
)


def test_memory_stores_messages():
    memory = AgentMemory(
        max_messages=4
    )

    memory.remember_user(
        "Hello"
    )

    memory.remember_assistant(
        "Hi"
    )

    messages = memory.messages()

    assert len(messages) == 2

    assert messages[0].role == "user"
    assert messages[0].content == "Hello"

    assert (
        messages[1].role
        == "assistant"
    )
    assert (
        messages[1].content
        == "Hi"
    )


def test_memory_is_bounded():
    memory = AgentMemory(
        max_messages=3
    )

    memory.remember_user(
        "message-1"
    )

    memory.remember_assistant(
        "message-2"
    )

    memory.remember_user(
        "message-3"
    )

    memory.remember_assistant(
        "message-4"
    )

    messages = memory.messages()

    assert len(messages) == 3

    assert [
        message.content
        for message in messages
    ] == [
        "message-2",
        "message-3",
        "message-4",
    ]


def test_memory_rejects_invalid_limit():
    with pytest.raises(
        ValueError
    ):
        AgentMemory(
            max_messages=0
        )


def test_memory_rejects_empty_content():
    memory = AgentMemory()

    with pytest.raises(
        ValueError
    ):
        memory.remember_user(
            "   "
        )


def test_memory_can_be_cleared():
    memory = AgentMemory()

    memory.remember_user(
        "hello"
    )

    memory.remember_assistant(
        "hi"
    )

    memory.clear()

    assert len(memory) == 0
    assert memory.messages() == ()