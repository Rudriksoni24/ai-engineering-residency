from local_llm.contracts import (
    BankingTransactionAnalysis,
)
from local_llm.runtime.ollama_runtime import OllamaRuntime
from local_llm.runtime.runtime_types import GenerationRequest


runtime = OllamaRuntime()

request = GenerationRequest(
    model="qwen2.5:3b",
    prompt="""
Analyze the following transaction.

Transaction ID: TXN-1001
Amount: 850000 INR
Country: India
Previous transactions from this customer:
12000, 15000, 18000 INR

Determine the risk level.
""",
    temperature=0,
    max_tokens=300,
)

result = runtime.generate_structured(
    request=request,
    response_model=BankingTransactionAnalysis,
)

print(result)
print(result.model_dump_json(indent=2))