"""Tests for the Local LLM runtime configuration."""

from local_llm.api.dependencies import get_llm_service


def test_default_ollama_endpoint(monkeypatch):
    """Local execution retains the existing default endpoint."""

    monkeypatch.delenv(
        "OLLAMA_BASE_URL",
        raising=False,
    )

    get_llm_service.cache_clear()

    try:
        service = get_llm_service()

        assert service.runtime.base_url == (
            "http://localhost:11434"
        )

    finally:
        get_llm_service.cache_clear()


def test_configured_ollama_endpoint(monkeypatch):
    """The endpoint can be configured externally."""

    monkeypatch.setenv(
        "OLLAMA_BASE_URL",
        "http://ollama.example.internal:11434",
    )

    get_llm_service.cache_clear()

    try:
        service = get_llm_service()

        assert service.runtime.base_url == (
            "http://ollama.example.internal:11434"
        )

    finally:
        get_llm_service.cache_clear()


def test_configured_endpoint_removes_trailing_slash(
    monkeypatch,
):
    """The existing runtime normalizes the base URL."""

    monkeypatch.setenv(
        "OLLAMA_BASE_URL",
        "http://ollama.example.internal:11434/",
    )

    get_llm_service.cache_clear()

    try:
        service = get_llm_service()

        assert service.runtime.base_url == (
            "http://ollama.example.internal:11434"
        )

    finally:
        get_llm_service.cache_clear()