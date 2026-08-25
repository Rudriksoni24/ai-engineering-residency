# Sprint 2 Day 7 — Local LLM Benchmark and Evaluation

## Objective

Evaluate local models and runtimes for specific workloads.

## Environment

- Machine: Apple Silicon M2
- Memory: 16 GB
- Runtime: Ollama
- Model: qwen2.5:3b

> Note: the runtime and model names above are carried over from the results CSV template and were not explicitly printed in the benchmark logs. Confirm these against `scripts/run_benchmark` before treating this report as final.

---

# Benchmark Methodology

## Test Cases

| Case | Purpose |
|---|---|
| Transformer Concept | Technical explanation |
| RAG Concept | AI knowledge |
| Structured Output | JSON reliability |
| Banking Reasoning | Domain reasoning |
| Concise Summary | Controlled output |

## Runs

Each test was executed 3 times via `uv run python -m scripts.run_benchmark`, run back-to-back on the same machine with no other workload changes between runs. One gap exists in the data: the second run's log ends mid-output during `banking_reasoning` and never reaches `concise_summary`, so that case has only 2 of 3 runs recorded. See [Limitations](#limitations-of-this-evaluation).

---

# Results

| Case | Model | Runtime | Avg Latency | Keyword Score | Valid JSON |
|---|---|---|---:|---:|---|
| Transformer Concept | qwen2.5:3b | Ollama | 2.43s | 0.44 | N/A |
| RAG Concept | qwen2.5:3b | Ollama | 2.15s | 1.00 | N/A |
| Structured Output | qwen2.5:3b | Ollama | 1.07s | N/A | 0 / 3 |
| Banking Reasoning | qwen2.5:3b | Ollama | 9.36s | 0.47 | N/A |
| Concise Summary | qwen2.5:3b | Ollama | 3.77s (n=2) | 0.67 | N/A |

Per-run figures are in `reports/sprint02/day07-results.csv`.

---

# Observations

## Latency

Latency scales with expected output length and reasoning depth rather than with case topic. `structured_output` was consistently fastest (0.81s–1.52s, avg 1.07s) since it only needs to emit a short JSON object. `banking_reasoning` was consistently the slowest by a wide margin (8.46s–9.94s, avg 9.36s) — roughly 4x the general-purpose cases — because it produces a longer, multi-part structured answer (five numbered factors with sub-explanations). `transformer_concept`, `rag_concept`, and `concise_summary` cluster in the 2–4s range, consistent with short, 3-bullet conceptual explanations. Run-to-run variance within a case (e.g., `transformer_concept` ranging 2.13s–2.99s) is within the range expected from local machine load rather than indicating a systemic issue.

## Structured Output Reliability

This is the weakest result in the benchmark: **all 3 runs failed JSON validation (0/3 valid)**. Looking at the raw outputs, the model's JSON content itself was well-formed in every run — the failure mode is that the model wrapped the object in a Markdown code fence (` ```json ... ``` `), and in the first run also prefixed it with an explanatory sentence ("Here is a sample JSON response..."). A strict parser expecting a raw JSON string will fail on both of these, even though the underlying data is correct. This is a formatting-instruction-following problem, not a data-correctness problem.

## Reasoning Quality

`banking_reasoning` scored 0.4, 0.6, and 0.4 (avg 0.47) — moderate and inconsistent. Qualitatively, all three responses were well-structured (five numbered factors, each with a short explanation) and covered sensible categories: transaction history/patterns, country or sanctions risk, fraud detection, and customer verification/communication. The score variance suggests the model doesn't reliably hit the same specific terms across runs — e.g., "sanctions," "IP address," and "regulatory compliance" appeared in some runs but not others — even though the overall reasoning quality looked comparable across all three by eye.

## Runtime Behavior

No crashes or errors were observed at the runtime/Ollama level across the three benchmark invocations. The one operational issue was procedural, not a model or runtime failure: the second run's captured log stops mid-sentence during `banking_reasoning`'s output and never records `concise_summary`, most likely from the log capture being cut short rather than the model failing to respond.

---

# Model Selection Decision

## Small Model

Use for:

- Short conceptual explanations (`transformer_concept`, `rag_concept`) where latency is under ~2.5s and keyword coverage was strong (RAG scored a perfect 1.0 on all 3 runs)
- Concise, bounded-length summaries (`concise_summary`) where output needs to stay short and responsive
- Any interactive/latency-sensitive path where "good enough" quality at sub-3-second response time matters more than exhaustive completeness

## Larger Model

Use for:

- Structured/JSON-output tasks, until formatting compliance improves — either via a larger model or stricter decoding (see Recommended Architecture)
- Domain reasoning tasks like `banking_reasoning` where completeness and consistency of coverage matter, given the current model's 0.4–0.6 keyword-score spread and ~9.4s latency already approaches a threshold where a larger, more capable model may be justified on quality grounds even at added latency cost

---

# Recommended Architecture

Route by task type rather than using one model for everything:

1. **Fast path (small local model, qwen2.5:3b via Ollama):** conceptual Q&A and bounded summaries, where this benchmark showed strong keyword coverage and low latency.
2. **Structured-output path:** keep the small model, but stop relying on raw string parsing. Either (a) post-process responses by stripping Markdown code fences before parsing, or (b) use Ollama's JSON-mode / grammar-constrained decoding so the model is forced to emit a bare JSON object. This is a low-cost fix that should take `valid_json` from 0/3 to near 3/3 without changing models.
3. **Domain-reasoning path (banking_reasoning and similar):** given the latency is already ~9.4s and quality is inconsistent, evaluate a larger local model or a hosted model for this path specifically, since the cost of an already-slow response failing to cover key risk factors is higher than the cost of the extra latency a bigger model would add.

---

# Limitations of This Evaluation

- Keyword matching does not measure correctness.
- Latency results depend on local machine conditions.
- Small sample size — only 3 runs per case, and `concise_summary` has only 2 recorded runs due to a truncated log in run 2, so its average latency and keyword score are less reliable than the other four cases.
- Prompt design influences results.
- Evaluation dataset is synthetic.
- Model and runtime identity for this report were inferred from the results template, not confirmed from the benchmark script itself.

---

# Key Learnings

- The small model's biggest weakness isn't reasoning content, it's output formatting — 0/3 valid JSON despite the underlying JSON being correct in every run, purely due to Markdown code-fence wrapping. This is a cheap, high-leverage fix (parsing or constrained decoding) before any model upgrade is needed.
- Latency scales with output complexity far more than with topic: reasoning-style tasks (`banking_reasoning`) cost ~4x the latency of short conceptual or summary tasks.
- Keyword-score variance on `banking_reasoning` (0.4–0.6) suggests the small model's reasoning coverage isn't fully stable run-to-run; a larger sample size would help confirm whether this is real variance or noise from only 3 runs.
- Logging/capture gaps (the missing `concise_summary` run 2) are a process risk worth fixing before scaling up run counts — an automated CSV writer per run would prevent this in future sprints.