# Sprint 2 — Day 6

# Local LLM API Service

## Goal

Build a typed HTTP service around the local LLM runtime.

## Learning Objectives

By the end of this day, I should understand:

- FastAPI fundamentals.
- HTTP API boundaries.
- Dependency injection.
- Request validation.
- Response contracts.
- Health and readiness checks.
- Runtime abstraction at the service layer.
- Why APIs should not directly depend on a specific model runtime.

## Deliverables

- [ ] FastAPI application.
- [ ] Health endpoint.
- [ ] Generation endpoint.
- [ ] Typed request contract.
- [ ] Typed response contract.
- [ ] LLM service layer.
- [ ] Runtime dependency.
- [ ] API tests.
- [ ] Local integration test.
- [ ] API report.

## Definition of Done

- [ ] API starts locally.
- [ ] Health endpoint works.
- [ ] Generation endpoint calls the local LLM.
- [ ] Invalid requests are rejected.
- [ ] Runtime is not directly coupled to routes.
- [ ] Tests pass.