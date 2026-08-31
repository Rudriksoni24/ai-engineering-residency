# Sprint 5 — Day 7
## Sprint Integration

### Artifact

Research and Analysis Agent

---

## Objective

Integrate the agent infrastructure built throughout Sprint 5 into a single
research-oriented application while preserving architectural boundaries.

---

## Learning Objectives

By the end of this day I should be able to explain:

- why an agent application should compose existing infrastructure
- capability layer vs orchestration layer
- search vs read tool separation
- why tool observations should be treated as evidence
- why multi-hop research naturally fits an iterative agent loop
- how memory, guardrails, tools, and evaluation interact
- why integration code should remain thin
- deterministic tests vs real-model behavioral evaluation
- why successful integration does not imply production readiness

---

## Sprint 5 Architecture

User
→ PromptBuilder
→ Generator
→ DecisionParser
→ DecisionGuard
→ ToolExecutor
→ Tool
→ Observation
→ ReActAgent
→ Final Response

Cross-cutting concerns:

Memory
Evaluation

---

## Research Workflow

A research question may require:

1. identifying relevant documents
2. retrieving the relevant document
3. reading its contents
4. connecting evidence from multiple sources
5. producing a final answer

Example:

Question:
Which architecture component validates tool arguments, and which component
controls whether a tool is permitted?

Possible trajectory:

search_knowledge("tool validation")
→ doc-tool-execution

read_document("doc-tool-execution")
→ executor validates arguments

search_knowledge("agent guardrails")
→ doc-guardrails

read_document("doc-guardrails")
→ guard controls policy

final
→ executor validates execution contract; guard controls application policy

---

## Search Tool vs Read Tool

Search answers:

"Which documents might contain relevant evidence?"

Read answers:

"What does this specific document say?"

These are different capabilities.

Combining them into one tool may be convenient, but separating them makes
agent behavior observable and testable.

---

## Application Composition

The ResearchAnalysisAgent should not implement its own reasoning loop.

It composes:

- AgentToolRegistry
- AgentToolExecutor
- AgentPromptBuilder
- AgentDecisionParser
- AgentDecisionGuard
- AgentMemory
- ReActAgent

The application layer configures infrastructure.

It does not duplicate infrastructure.

---

## Evidence Discipline

Tool observations are evidence.

The model should not invent facts that are absent from observations.

If additional evidence is required, the agent should call another tool.

If sufficient evidence already exists, the agent should return final.

---

## Evaluation

The integrated agent should be evaluated on:

- answer evidence
- expected tool usage
- trajectory where appropriate
- maximum steps
- controlled failures

Evaluation remains outside runtime execution.

---

## Not Production RAG

The research corpus today is deliberately deterministic and in-memory.

We are not adding:

- embeddings
- vector databases
- GraphRAG
- internet search
- document chunking
- ranking models
- rerankers
- citations
- distributed tool execution

Those belong to later systems.

---

## Exit Criteria

I can explain how every Sprint 5 component participates in an end-to-end
agent request.

I can trace:

user query
→ model decision
→ guardrail
→ executor
→ tool observation
→ next decision
→ final answer
→ memory
→ evaluation

I can explain why the integration application remains thin.

I can run the complete repository regression successfully.