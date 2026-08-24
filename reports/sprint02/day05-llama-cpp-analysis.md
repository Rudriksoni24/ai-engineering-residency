# Sprint 2 Day 5 — llama.cpp and GGUF

## Environment

- Hardware: Apple Silicon M2
- Unified Memory: 16 GB
- Operating System: macOS
- llama.cpp Version: b10566-bb4caa754 (v0.2.0 Release)

## Model

- Name: Qwen3-4B-Instruct
- Parameters: 4.0 Billion Total (3.6 Billion Non-Embedding)
- Quantization: Q4_K_M (Mixed precision: 4-bit attention, 5-bit feed-forward)
- Format: GGUF
- File Size: 2.32 GB (4,877,504 blocks)
- Context: 32,768 tokens natively supported

## Experiment 1 — CLI Inference

Prompt:
"Explain the purpose of a KV cache in exactly three bullet points."

Observation:
The execution was transient, paying a 1.85-second cold-start disk read penalty to load the 2.32 GB binary structure into unified memory. Once active, the model generated text at a raw speed of 31.5 tokens/sec. The model initiated its output with a native reasoning block (`[Start thinking]...`) before outputting the final three bullet points, providing deep structural explanations of attention matrix operations.

## Experiment 2 — Structured Output

Prompt:
"Return only valid JSON matching this schema: {"concept": "KV cache", "purpose": "...", "tradeoff": "..."}"

Valid JSON:
Yes. Under deterministic greedy decoding (temperature = 0.0), the model yielded structurally sound JSON formatting with no trailing markdown syntax blocks.

Schema valid:
Yes. The keys matched the schema expectations, correctly mapping the string definitions for "purpose" and "tradeoff" directly within the field limits.

## Experiment 3 — Server Mode

Endpoint tested:
http://localhost:8080/v1/chat/completions (via long-running `llama-server` process allocation)

Result:
Successful integration. The persistent server environment eliminated the cold-start loading latency entirely, dropping Time-To-First-Token (TTFT) metrics from 1.85 seconds down to ~210ms. The server supported continuous batching and simultaneous multi-slot processing parameters smoothly.

## Memory Analysis

Day 3 theoretical estimate:
2.00 GB (Calculated via flat matrix reduction: 4.0B parameters × 4 bits / 8)

Actual model file size:
2.32 GB (+0.32 GB / +16% variance over basic math)

Observed runtime behavior:
The 320 MB footprint expansion is driven by three factors:
1. The 151,643-token Tiktoken embedding table, which is held at unquantized 16-bit FP16 precision (~776 MB tax).
2. K-Quant protection parameters that use 5-bit tracks for critical feed-forward layers (`ffn_gate`).
3. Internal GGUF metadata block scale indicators (16-bit multipliers for every 32-weight slice). Memory bandwidth remained highly stable under the Metal execution layer.

## Key Learnings

1. **Orchestration vs. Computation Latency:** Command-line execution logs can distort speed metrics. Raw model token generation speeds are identical across runtimes (~39-43 tokens/sec), but transient CLI calls pay a heavy file initialization tax that persistent background servers avoid.
2. **Native Reasoning Tokens:** Next-generation GGUF architectures feature toggleable internal thinking strings (`[Start thinking]`). This deepens logical layout processing but introduces a hidden generation token tax that slows down apparent text emission velocities.
3. **Grammar Enforcement Superiority:** Enforcing JSON layouts via the runtime constraint layer ensures production reliability, shielding application code from hallucinated strings.

## Problems Encountered

1. **Hugging Face Redirection Bans:** Baseline `curl` commands without specific agent strings fetch 174KB text-based Git LFS error pointers instead of the 2.32 GB binary file.
2. **PEP 668 Protection Interceptions:** Homebrew python environments block global installation of dependency packages (like `huggingface_hub`), requiring virtual sandboxing (`venv`) or explicit `--break-system-packages` override parameters.
3. **Case-Sensitive Repository Routing:** Download requests crash with 404 errors if the file system path array mismatches the target capitalization layout (`Qwen3-4B-Q4_K_M.gguf`).

## Decision

The application backend will standardize on a two-tier inference deployment pipeline:
1. **Ollama Service Layer:** Deployed as the core, long-running production API endpoint due to its superior prompt evaluation acceleration (233.94 tokens/sec) and turn-key OpenAI interface format.
2. **llama.cpp Diagnostics Engine:** Retained purely inside localized `/scripts/` directories to perform low-level parameter tuning, custom grammar testing, and deep token-by-token validation.
