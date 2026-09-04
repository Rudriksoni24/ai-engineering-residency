from __future__ import annotations

from typing import Any

from workflows.contracts.state import (
    WorkflowState,
    WorkflowStatus,
    WorkflowTransition,
)


def workflow_state_to_dict(
    state: WorkflowState,
) -> dict[str, Any]:
    return {
        "workflow_id": state.workflow_id,
        "status": state.status.value,
        "input": state.input,
        "context": state.context,
        "result": state.result,
        "error": state.error,
        "history": [
            {
                "source": transition.source.value,
                "destination": transition.destination.value,
            }
            for transition in state.history
        ],
    }


def workflow_state_from_dict(
    data: dict[str, Any],
) -> WorkflowState:
    history = [
        WorkflowTransition(
            source=WorkflowStatus(item["source"]),
            destination=WorkflowStatus(item["destination"]),
        )
        for item in data.get("history", [])
    ]

    return WorkflowState(
        workflow_id=str(data["workflow_id"]),
        status=WorkflowStatus(data["status"]),
        input=dict(data.get("input", {})),
        context=dict(data.get("context", {})),
        result=data.get("result"),
        error=data.get("error"),
        history=history,
    )