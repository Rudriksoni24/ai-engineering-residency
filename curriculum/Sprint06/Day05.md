# Sprint 6 — Day 5: Human-in-the-Loop

## Artifact

Approval Workflow

## Learning Objectives

By the end of this day I should understand:

- why some workflow actions require human approval
- why approval must be represented as explicit workflow state
- the difference between pending, approved and rejected approval states
- why workflow execution must suspend while approval is pending
- why approve and reject should be explicit application APIs
- why production workflow engines should not use input()
- how approval state can survive a process restart
- how approval integrates with workflow checkpoints
- how protected execution resumes only after approval
- how rejected actions remain blocked
- how approval events can be observed without storing hidden reasoning

## Human-in-the-Loop

Some operations should not execute automatically.

Examples:

- transfer large amounts of money
- delete production resources
- issue refunds above a limit
- send external communications
- modify sensitive records

The system may determine what action should happen while still requiring a human
to authorize execution.

## Approval Lifecycle

A simple lifecycle is:

NONE
  ↓
PENDING
  ├── APPROVED
  └── REJECTED

Pending means workflow execution is suspended at a protected boundary.

Approved means the protected operation may continue.

Rejected means the protected operation must not execute.

## Approval Request

An approval request should contain explicit metadata such as:

- approval ID
- workflow ID
- protected action
- reason for approval
- arbitrary safe metadata
- current decision state

## Suspension

Suspension is not the same as failure.

A pending workflow has not failed.

It is waiting for an external decision.

## Persistence

Approval state must be serializable.

If the workflow process terminates while waiting:

Process A
  ↓
PENDING APPROVAL
  ↓
Checkpoint Store

Process terminates.

Process B
  ↓
Load checkpoint
  ↓
Still PENDING APPROVAL

The system must not forget that authorization was required.

## Explicit APIs

Approval should be performed through APIs such as:

approve(workflow_id)
reject(workflow_id)

The engine itself should not call input().

A CLI may use input() as an interface and then call the API, but interactive
input is not workflow-engine logic.

## Guarded Resume

Persistent resume alone is not sufficient after human approval is introduced.

Before resuming protected execution, the workflow layer must check:

PENDING  -> block
APPROVED -> allow
REJECTED -> block

## Day 5 Boundary

Today implements:

- approval contracts
- pending approval
- approval persistence
- explicit approve API
- explicit reject API
- guarded workflow resume
- protected action suspension
- approval metadata
- deterministic tests

Today does NOT implement:

- retries
- backoff
- transient failure recovery
- parallel approvals
- quorum approval
- role-based authorization