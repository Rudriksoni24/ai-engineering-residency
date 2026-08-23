from unittest.mock import Mock, patch

from runtime.ollama_runtime import OllamaRuntime
from runtime.runtime_types import GenerationRequest


def test_health_check_returns_false_when_runtime_unavailable():
    runtime = OllamaRuntime(
        base_url="http://localhost:9999",
    )

    assert runtime.health_check() is False


@patch("runtime.ollama_runtime.requests.post")
def test_generate_returns_generation_response(mock_post):
    mock_response = Mock()

    mock_response.json.return_value = {
        "response": "Hello from local model",
        "model": "test-model",
        "prompt_eval_count": 10,
        "eval_count": 5,
        "total_duration": 100,
        "load_duration": 20,
        "eval_duration": 50,
    }

    mock_post.return_value = mock_response

    runtime = OllamaRuntime()

    request = GenerationRequest(
        model="test-model",
        prompt="Hello",
    )

    response = runtime.generate(request)

    assert response.text == "Hello from local model"
    assert response.model == "test-model"
    assert response.prompt_tokens == 10
    assert response.completion_tokens == 5