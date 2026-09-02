from workflows.contracts.state import WorkflowState, WorkflowStatus
from workflows.core.state_machine import WorkflowStateMachine


def main() -> None:
    state = WorkflowState.create(
        {
            "task": "review account activity",
            "account_id": "ACC001",
        },
        workflow_id="workflow-demo-001",
    )

    machine = WorkflowStateMachine(state)

    print("Workflow created")
    print(f"ID: {machine.state.workflow_id}")
    print(f"Status: {machine.status.value}")
    print()

    machine.transition_to(WorkflowStatus.PLANNING)

    print("Planning complete")
    print(f"Status: {machine.status.value}")
    print()

    machine.transition_to(WorkflowStatus.EXECUTING)

    print("Execution started")
    print(f"Status: {machine.status.value}")
    print()

    machine.complete(
        {
            "message": "Account activity review completed.",
        }
    )

    print("Workflow completed")
    print(f"Status: {machine.status.value}")
    print(f"Result: {machine.state.result}")
    print()

    print("Transition history")

    for index, transition in enumerate(machine.history, start=1):
        print(
            f"{index}. "
            f"{transition.source.value} "
            f"-> "
            f"{transition.destination.value}"
        )


if __name__ == "__main__":
    main()

    #uv run python -m workflows.scripts.run_state_machine
