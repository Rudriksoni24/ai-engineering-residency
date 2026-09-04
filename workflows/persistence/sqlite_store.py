from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from workflows.persistence.contracts import (
    WorkflowCheckpoint,
)
from workflows.persistence.serialization import (
    workflow_state_from_dict,
    workflow_state_to_dict,
)


class SQLiteCheckpointStore:
    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        self._database_path = str(database_path)
        self._initialize()

    def save(
        self,
        checkpoint: WorkflowCheckpoint,
    ) -> None:
        state_json = json.dumps(
            workflow_state_to_dict(checkpoint.state)
        )

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO workflow_checkpoints (
                    workflow_id,
                    state_json,
                    next_node,
                    completed
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(workflow_id)
                DO UPDATE SET
                    state_json = excluded.state_json,
                    next_node = excluded.next_node,
                    completed = excluded.completed
                """,
                (
                    checkpoint.workflow_id,
                    state_json,
                    checkpoint.next_node,
                    int(checkpoint.completed),
                ),
            )

    def load(
        self,
        workflow_id: str,
    ) -> WorkflowCheckpoint | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    workflow_id,
                    state_json,
                    next_node,
                    completed
                FROM workflow_checkpoints
                WHERE workflow_id = ?
                """,
                (workflow_id,),
            ).fetchone()

        if row is None:
            return None

        state_data = json.loads(row["state_json"])

        return WorkflowCheckpoint(
            workflow_id=row["workflow_id"],
            state=workflow_state_from_dict(state_data),
            next_node=row["next_node"],
            completed=bool(row["completed"]),
        )

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                    workflow_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    next_node TEXT NOT NULL,
                    completed INTEGER NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self._database_path
        )

        connection.row_factory = sqlite3.Row

        return connection