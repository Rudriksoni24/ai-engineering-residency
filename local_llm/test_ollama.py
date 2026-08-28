from local_llm.runtime.ollama_runtime import OllamaRuntime
from local_llm.runtime.runtime_types import GenerationRequest


runtime = OllamaRuntime()

request = GenerationRequest(
    model="qwen2.5:3b",
    prompt="Explain the difference between an LLM model and an LLM runtime.",
    max_tokens=200,
    temperature=0.2,
)

print("Health:", runtime.health_check())

response = runtime.generate(request)

print("\nResponse:")
print(response.text)

print("\nModel:")
print(response.model)

print("\nPrompt Tokens:")
print(response.prompt_tokens)

print("\nCompletion Tokens:")
print(response.completion_tokens)

print("\nMetadata:")
print(response.metadata)