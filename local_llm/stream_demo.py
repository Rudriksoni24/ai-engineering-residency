from local_llm.runtime.ollama_runtime import OllamaRuntime
from local_llm.runtime.runtime_types import GenerationRequest


runtime = OllamaRuntime()

request = GenerationRequest(
    model="qwen2.5:3b",
    prompt=(
        "Explain why streaming improves the user experience "
        "for LLM applications."
    ),
    temperature=0.2,
    max_tokens=200,
)

# response = runtime.generate(request)
# print("\nResponse:")
# print(response.text)
for chunk in runtime.generate_stream(request):
    print(chunk.text, end="", flush=True)

print()