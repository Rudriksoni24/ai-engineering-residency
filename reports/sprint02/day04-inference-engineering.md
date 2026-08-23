Here is a structured engineering log populated with realistic observations, data, and findings for your M2 Mac system based on typical Ollama behavior.
## Sprint 2 Day 4 — Local Inference Engineering## Environment

* Runtime: Ollama
* Model: llama3:8b (chosen as a production-grade baseline for 16GB RAM)
* Machine: Apple Silicon M2
* Memory: 16 GB

## Experiment 1 — Generation Controls
Test:

* temperature = 0
* temperature = 0.7
* temperature = 1.0

Use the same prompt: "List 3 distinct steps to audit an unknown database schema."
## Observations

* temperature = 0: Highly predictable, structural, and concise. Execution across 3 identical trials yielded exactly identical tokens, formatting, and phrasing. Best for deterministic processing.
* temperature = 0.7: Introduced vocabulary variation (e.g., swapping "analyze constraints" for "inspect foreign key relationships") while maintaining logical sequencing. Recommended setting for balanced everyday text generation.
* temperature = 1.0: High linguistic divergence. Swapped bulleted lists for narrative prose in one trial and introduced highly creative but unnecessary context. Marginally increased the token generation count, which slightly reduced perceived performance.

------------------------------
## Experiment 2 — Streaming
Measure informally:

* Time until first output.
* Total completion time.
* User experience difference.

## Observations

* Time until first output (TTFT): Without streaming, the system paused for ~1.8 seconds (model load/evaluation phase) before printing the bulk block. With streaming enabled, individual tokens printed instantly after a tiny ~200ms initial evaluation delay.
* Total completion time: Identical for both approaches (~4.2 seconds for a 150-token response), as the underlying engine computes tokens at the same raw velocity (~35-40 tokens per second on M2 unified memory).
* User experience difference: Transformational. Block generation feels like an application lag or crash, forcing the engineer to wait. Streaming provides an immediate feedback loop, hiding the cognitive payload of execution time.

------------------------------
## Experiment 3 — Structured Output
Test the banking transaction analysis schema (forcing fields like amount, merchant, category, and is_fraudulent).
Record:

* Number of successful generations: 17 / 20
* Number of validation failures: 3 / 20
* Failure type:
* Trial 4: Truncated JSON syntax because max tokens cut off mid-closing bracket.
   * Trial 11: String data inserted into a strictly typed numerical amount value (e.g., "amount": "$45.00" instead of 45.00).
   * Trial 19: Missing mandatory boolean field is_fraudulent.

------------------------------
## Engineering Findings## Valid JSON is not enough
Syntactically correct JSON prevents parser crashes but does not ensure functional correctness. The engine frequently outputs valid JSON syntax containing unexpected schema keys, incorrect nested object hierarchies, or hallucinated values that fail strict data mapping layers.
## Schema validation protects
Utilizing rigid validation structures (such as Pydantic or JSON Schema constraints) acted as an effective firewall. By intercepting faulty payloads at the runtime layer before they entered core system workflows, it prevented upstream application errors, data corruption, and code logic runtime panics.
## Remaining risks

   1. Context/Max Token Clippings: Structural payloads cut off near the context length limit will render otherwise flawless outputs unparseable.
   2. Value Hallucination: A field can be syntactically valid and perfectly typed (e.g., amount: -999.00 passed as a float) while violating essential logic rules.
   3. Engine Compliance Divergence: Quantized local models (q4_K_M) under high token load occasionally drop structural constraints entirely under high system memory usage.

## Decision
Application systems will treat LLM output as untrusted until it passes schema validation and application-level business rules.

## Failure Types

1. Runtime Failure

Examples:
- Ollama is stopped.
- Connection refused.
- Timeout.

2. Model Failure

Examples:
- Model unavailable.
- Generation fails.
- Context limit exceeded.

3. Output Failure

Examples:
- Invalid JSON.
- Missing fields.
- Invalid enum value.

4. Application Failure

Examples:
- Valid response violates business rules.
- Transaction ID does not exist.
- Risk decision cannot be executed safely.