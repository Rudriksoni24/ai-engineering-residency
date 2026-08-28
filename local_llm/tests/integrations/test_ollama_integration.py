from local_llm.runtime.ollama_runtime import OllamaRuntime
from local_llm.runtime.runtime_types import GenerationRequest


def test_real_ollama_generation():
    """Live system-wide integration test confirming connectivity to a local Ollama daemon."""
    runtime = OllamaRuntime()

    # 1. Verify the background daemon service is responsive
    assert runtime.health_check(), "Ollama daemon is not running on http://localhost:11434"

    # 2. Issue a strict, short generation request to a known model footprint
    request = GenerationRequest(
        model="qwen2.5:3b ",  # Using the 0.5b model we pulled earlier for stable context execution
        prompt="Respond with exactly: LOCAL_LLM_WORKING",
        max_tokens=20,
        temperature=0,
    )

    # 3. Process the live hardware inference
    response = runtime.generate(request)

    # 4. Check for absolute output compliance
    assert "LOCAL_LLM_WORKING" in response.text, f"Unexpected response text: {response.text}"
