import pytest

from runtime.base import LLMRuntime
from runtime.runtime_types import GenerationRequest, GenerationResponse

from collections.abc import Iterator
from runtime.streaming import StreamChunk 

# =====================================================================
# Tests: Runtime Contract Types
# =====================================================================

def test_generation_request_creation():
    """[x] GenerationRequest can be created."""
    req = GenerationRequest(prompt="Hello", model="llama3")
    assert req.prompt == "Hello"
    assert req.model == "llama3"


def test_generation_request_defaults():
    """[x] Default values are correct."""
    req = GenerationRequest(prompt="Test", model="mistral")
    assert req.max_tokens == 256
    assert req.temperature == 0.7


def test_generation_response_creation():
    """[x] GenerationResponse can be created."""
    res = GenerationResponse(text="World", model="llama3")
    assert res.text == "World"
    assert res.model == "llama3"


def test_generation_response_metadata_absent():
    """[x] Metadata can be absent (defaults to an empty dictionary)."""
    res = GenerationResponse(text="No metadata", model="llama3")
    assert res.metadata is None


def test_generation_response_metadata_present():
    """[x] Metadata can contain inference information."""
    inference_meta = {"finish_reason": "stop", "seed": 42}
    res = GenerationResponse(
        text="With metadata",
        model="llama3",
        prompt_tokens=10,
        completion_tokens=20,
        metadata=inference_meta
    )
    assert res.prompt_tokens == 10
    assert res.completion_tokens == 20
    assert res.metadata["finish_reason"] == "stop"
    assert res.metadata["seed"] == 42


# =====================================================================
# Tests: Abstraction Boundary (Fake Runtime Verification)
# =====================================================================

class FakeRuntime(LLMRuntime):
    """A minimal mock runtime to test contract conformance."""

    def __init__(self, healthy: bool = True):
        self.is_healthy = healthy

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(
            text=f"Response to: {request.prompt}",
            model=request.model,
            prompt_tokens=5,
            completion_tokens=12,
            metadata={"mocked": True}
        )

    def generate_stream(
        self,
        request: GenerationRequest,
    ) -> Iterator[StreamChunk]:
        """Fake implementation to satisfy the abstract contract."""
        yield StreamChunk(text="fake chunk", done=True)

    def health_check(self) -> bool:
        return self.is_healthy


def test_fake_runtime_implements_contract():
    """[x] Fake runtime implements the contract."""
    runtime = FakeRuntime()
    assert isinstance(runtime, LLMRuntime)


def test_fake_runtime_generate_returns_response():
    """[x] generate returns GenerationResponse."""
    runtime = FakeRuntime()
    request = GenerationRequest(prompt="Ping", model="test-model")
    response = runtime.generate(request)
    
    assert isinstance(response, GenerationResponse)
    assert response.text == "Response to: Ping"
    assert response.model == "test-model"


def test_fake_runtime_health_check_returns_boolean():
    """[x] health_check returns a boolean."""
    healthy_runtime = FakeRuntime(healthy=True)
    unhealthy_runtime = FakeRuntime(healthy=False)
    
    assert healthy_runtime.health_check() is True
    assert unhealthy_runtime.health_check() is False
