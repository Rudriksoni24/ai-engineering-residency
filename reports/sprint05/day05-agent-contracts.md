# Sprint 5 — Day 5 Report
## Structured Outputs and Guardrails

### Artifact

Reliable Agent Contracts

---

## Objective

Harden the boundary between model-generated decisions and application
execution using deterministic application-side validation.

---

## What I Built

Implemented:

- AgentGuardrailConfig
- AgentDecisionGuard
- AgentGuardrailError
- final-answer length validation
- registered-tool enforcement
- blocked-tool policy
- tool argument-count limits
- fail-closed decision validation
- optional ReActAgent guardrail integration
- guardrail-safe conversational memory behavior
- deterministic unit tests
- deterministic integration tests
- guarded local Ollama demonstration

---

## Validation Pipeline

Model output
→ AgentDecisionParser
→ AgentDecision
→ AgentDecisionGuard
→ AgentToolExecutor
→ observation

---

## Responsibility Boundaries

### AgentDecisionParser

Responsible for:

- parsing model output
- validating decision representation
- rejecting malformed structured output

### AgentDecisionGuard

Responsible for:

- application policy
- registered-tool validation
- blocked-tool policy
- structural limits
- final-answer limits

### AgentToolExecutor

Responsible for:

- required argument validation
- primitive type validation
- undeclared argument rejection
- tool execution
- converting runtime failures into ToolResult

---

## Core Principle

A valid LLM-generated tool request is not execution permission.

The model proposes actions.

Application code determines whether those actions are allowed.

---

## Fail-Closed Behavior

Unknown tools, blocked tools, excessive argument counts, and oversized final
answers are rejected before execution or final-response commitment.

Guardrail failures become controlled AgentExecutionError exceptions.

---

## Memory Interaction

Guardrail validation occurs before successful conversational memory commit.

Therefore rejected agent decisions do not become completed conversation
history.

---

## Backward Compatibility

AgentDecisionGuard is optional in ReActAgent.

Existing Day 3 and Day 4 agent behavior remains available when no guard is
configured.

---

## Testing

Added deterministic tests covering:

- accepted final decisions
- final-answer size rejection
- accepted registered tools
- unknown-tool rejection
- blocked-tool rejection
- argument-count rejection
- invalid guardrail configuration
- ReActAgent guard integration
- memory rollback on guardrail failure
- optional guardrail backward compatibility

---

## Limitations

Current guardrails do not provide:

- prompt-injection detection
- authentication
- authorization services
- PII detection
- human approval
- sandboxing
- rate limiting
- moderation
- semantic policy classifiers
- external policy engines

These are intentionally outside Day 5 scope.

---

## Key Takeaway

Structured output makes LLM decisions machine-readable.

Guardrails make application policy deterministic.

Reliable agents require both.