from __future__ import annotations

from workflows.coordination.contracts import (
    WorkerAgent,
)


class WorkerAlreadyRegisteredError(
    ValueError
):
    pass


class WorkerNotFoundError(
    LookupError
):
    pass


class WorkerRegistry:
    def __init__(self) -> None:
        self._workers: dict[str, WorkerAgent] = {}

    @property
    def worker_names(self) -> tuple[str, ...]:
        return tuple(self._workers)

    def register(
        self,
        worker: WorkerAgent,
    ) -> None:
        if not worker.name:
            raise ValueError(
                "Worker name cannot be empty."
            )

        if worker.name in self._workers:
            raise WorkerAlreadyRegisteredError(
                f"Worker {worker.name!r} "
                "is already registered."
            )

        self._workers[worker.name] = worker

    def get(
        self,
        worker_name: str,
    ) -> WorkerAgent:
        try:
            return self._workers[
                worker_name
            ]
        except KeyError as exc:
            raise WorkerNotFoundError(
                f"Worker {worker_name!r} "
                "is not registered."
            ) from exc