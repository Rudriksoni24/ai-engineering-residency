from unittest.mock import Mock, patch

import pytest

from graphrag.generation.ollama_generator import (
    OllamaGenerator,
)


def test_ollama_generator_returns_response():

    mock_response = Mock()

    mock_response.json.return_value = {
        "response": (
            "ACC001 initiated TXN001."
        )
    }

    mock_response.raise_for_status = (
        Mock()
    )

    with patch(
        "graphrag.generation."
        "ollama_generator.httpx.post",
        return_value=mock_response,
    ) as mock_post:

        generator = OllamaGenerator(
            model="test-model"
        )

        result = generator.generate(
            "test prompt"
        )

    assert (
        result
        == "ACC001 initiated TXN001."
    )

    mock_post.assert_called_once()


def test_ollama_generator_rejects_empty_prompt():

    generator = OllamaGenerator(
        model="test-model"
    )

    with pytest.raises(
        ValueError,
        match="prompt cannot be empty",
    ):
        generator.generate("")


def test_ollama_generator_rejects_empty_model():

    with pytest.raises(
        ValueError,
        match="model cannot be empty",
    ):
        OllamaGenerator(
            model=""
        )


def test_ollama_generator_rejects_empty_response():

    mock_response = Mock()

    mock_response.json.return_value = {
        "response": ""
    }

    mock_response.raise_for_status = (
        Mock()
    )

    with patch(
        "graphrag.generation."
        "ollama_generator.httpx.post",
        return_value=mock_response,
    ):

        generator = OllamaGenerator(
            model="test-model"
        )

        with pytest.raises(
            RuntimeError,
            match=(
                "Ollama returned an "
                "empty response"
            ),
        ):
            generator.generate(
                "test prompt"
            )