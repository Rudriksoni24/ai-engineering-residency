# Sprint 5 — Day 5
## Structured Outputs and Guardrails

### Artifact

Reliable Agent Contracts

---

## Learning Objectives

By the end of this day I should be able to explain:

- why JSON parsing alone is insufficient for reliable agents
- syntax validation vs semantic validation
- structured agent decision contracts
- tool allowlisting
- tool blocking policies
- output-size limits
- argument-count limits
- why prompt instructions are not security boundaries
- why application code owns execution permission
- why guardrail failures should not mutate conversational memory
- parser vs guardrail vs executor responsibilities

---

## Core Mental Model

The LLM proposes.

The application validates.

The application authorizes.

The application executes.

A model-generated tool request is never execution permission.

---

## Structured Decision Pipeline

Raw model output
→ AgentDecisionParser
→ AgentDecision
→ AgentDecisionGuard
→ AgentToolExecutor
→ observation

Each layer has a different responsibility.

---

## Parser Responsibility

The parser asks:

"Can this model output be interpreted as a valid AgentDecision?"

Examples:

- valid JSON
- supported decision type
- tool name is represented correctly
- tool arguments are an object
- final answer exists

This is structural validation.

---

## Guardrail Responsibility

The guard asks:

"Even if this is structurally valid, should the application allow it?"

Examples:

- requested tool must be registered
- requested tool must not be blocked by policy
- final answer must stay within configured limits
- tool argument count must remain within configured limits

This is application policy validation.

---

## Executor Responsibility

The executor asks:

"Can this specific tool call actually execute?"

Examples:

- required arguments exist
- argument types are correct
- undeclared arguments are rejected
- runtime exceptions become controlled ToolResult failures

---

## Why Prompt Instructions Are Not Guardrails

A prompt may say:

"Never call dangerous_tool."

The model can still return:

{
  "type": "tool",
  "tool_name": "dangerous_tool",
  "arguments": {}
}

Prompt instructions are model guidance.

Application validation is enforcement.

---

## Fail Closed

When the application cannot confidently validate a decision,
the safe default is rejection.

Rejecting uncertain actions is called failing closed.

---

## Memory Interaction

A rejected agent decision is not a successfully completed conversation turn.

Therefore guardrail failures should not be committed to agent memory.

---

## Not Implemented Today

We deliberately do not add:

- prompt injection classifiers
- PII detection
- authentication
- business authorization services
- human approval
- sandboxing
- rate limiting
- content moderation
- agent evaluation metrics
- production policy engines

Those belong to separate layers.

---

## Exit Criteria

I can explain:

- parser vs guardrail vs executor
- why valid JSON can still be rejected
- why application code owns execution authorization
- why prompts cannot enforce security
- why guardrails should fail closed
- why rejected turns should not be committed to memory

I can implement:

- immutable guardrail configuration
- final-answer limits
- registered-tool enforcement
- blocked-tool policy
- tool argument-count limits
- ReActAgent guardrail integration
- deterministic guardrail tests