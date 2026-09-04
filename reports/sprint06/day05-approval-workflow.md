# Sprint 6 — Day 5 Report

## Title

Human-in-the-Loop

## Artifact

Approval Workflow

## Objective

Introduce durable human approval checkpoints that suspend protected workflow
execution until an explicit decision is received.

## Implemented

- ApprovalStatus
- ApprovalRequest
- approval metadata
- ApprovalManager
- explicit request_approval API
- explicit approve API
- explicit reject API
- durable pending approval
- checkpoint preservation
- ApprovalWorkflowEngine
- guarded workflow resume
- pending-workflow suspension
- rejected-workflow protection
- completed approval decision validation
- deterministic approval tests
- process-restart approval tests

## Approval Lifecycle

PENDING
  ├── APPROVED
  └── REJECTED

Only pending approvals may receive a decision.

Approved and rejected decisions are terminal for the current approval.

## Suspension Model

A workflow awaiting approval persists:

- workflow state
- approval metadata
- protected next node

The Python process does not need to remain alive while approval is pending.

## Protected Resume

ApprovalWorkflowEngine checks the persisted approval before delegating execution
to PersistentWorkflowEngine.

PENDING:

resume is blocked.

APPROVED:

resume is allowed.

REJECTED:

resume is blocked.

## Persistence

Approval data is stored inside serializable workflow context.

Existing checkpoint persistence from Day 3 therefore persists approval without
introducing a new storage technology.

## Engine API

The workflow domain exposes explicit:

- request_approval()
- approve()
- reject()
- resume()

The production workflow engine does not call input().

## Process Restart

Tests prove pending and approved decisions survive new SQLite store, approval
manager and workflow-engine instances.

## Intentionally Deferred

Not implemented today:

- retries
- backoff
- transient failure handling
- multiple approvers
- quorum approval
- authentication/authorization
- distributed compare-and-set
- timestamps/audit identity

## Validation

uv run pytest workflows/tests/test_approval.py -v
uv run pytest workflows/tests -v
uv run pytest agents/tests -v
uv run pytest -v

If configured:

uv run ruff check workflows agents

## Result

Sprint 6 Day 5 introduces a durable human-in-the-loop boundary that prevents
protected operations from executing until an explicit persisted approval is
granted.