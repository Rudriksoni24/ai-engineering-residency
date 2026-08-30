# Sprint 5 — Day 6
## Agent Evaluation

### Artifact

Agent Test Harness

---

## Learning Objectives

By the end of this day I should be able to explain:

- why unit tests alone are insufficient for agent systems
- deterministic evaluation vs model-based evaluation
- exact-match vs keyword-based checks
- tool-use evaluation
- trajectory evaluation
- controlled-failure evaluation
- per-case metrics vs aggregate metrics
- why evaluation should be separated from runtime agent logic
- why non-deterministic model demos should not be the only correctness signal
- why evaluation datasets must represent expected behavior explicitly

---

## Core Mental Model

Traditional software often tests:

input → deterministic function → expected output

Agent systems often behave like:

input
→ model decision
→ tool call
→ observation
→ model decision
→ final output

Therefore evaluation must inspect more than the final string.

---

## What Can We Evaluate?

### Final answer

Did the response contain the expected information?

### Tool usage

Did the agent call the expected tool?

### Tool sequence

Did tools occur in the expected order?

### Iteration count

Did the agent complete within an acceptable number of steps?

### Controlled failure

Did invalid behavior fail in the expected application-controlled way?

---

## Deterministic Evaluation

Today our evaluation logic is deterministic.

Examples:

- required keywords
- expected tool names
- expected tool sequence
- maximum allowed steps
- expected success or failure

These checks are reproducible.

---

## Why Not LLM-as-Judge Yet?

LLM-based evaluation can be useful for:

- semantic correctness
- style
- reasoning quality
- nuanced comparisons

But it introduces:

- evaluator nondeterminism
- extra cost
- extra latency
- judge-model bias
- evaluation prompt design problems

Therefore Day 6 starts with deterministic evaluation.

---

## Unit Tests vs Evaluation Harness

Unit tests verify implementation behavior.

The evaluation harness measures agent behavior against a reusable set of
behavioral cases.

The same evaluation cases can later be executed against:

- deterministic fake generators
- local Ollama models
- hosted models
- different prompts
- different agent configurations

---

## Evaluation Case

An evaluation case should define:

- case ID
- user query
- expected success or failure
- required answer keywords
- expected tools
- optional exact tool sequence
- optional maximum steps

---

## Evaluation Result

A result should record:

- case ID
- passed or failed
- final answer
- actual tools
- number of steps
- failure message
- individual check results

---

## Aggregate Metrics

Useful initial metrics include:

- total cases
- passed cases
- failed cases
- pass rate
- average steps on successful cases

---

## Important Limitation

Keyword coverage does not prove semantic correctness.

For example:

Expected keywords:

Ravi Sharma
ACC001

An answer could contain both while still being misleading.

Today's evaluator is intentionally simple and deterministic.

---

## Exit Criteria

I can explain:

- tests vs evaluations
- final-answer evaluation vs trajectory evaluation
- deterministic checks vs LLM-as-judge
- why tool traces matter
- why aggregate pass rate alone can hide failure modes
- why evaluation logic must remain outside ReActAgent

I can implement:

- reusable evaluation case contracts
- reusable evaluation result contracts
- deterministic answer checks
- tool usage checks
- tool sequence checks
- step-budget checks
- controlled-failure checks
- evaluation summaries
- deterministic test coverage