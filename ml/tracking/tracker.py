from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow import ActiveRun, MlflowClient
from sklearn.pipeline import Pipeline


@dataclass(frozen=True)
class MLflowTrackingConfig:
    tracking_uri: str
    artifact_root: str
    experiment_name: str


@dataclass(frozen=True)
class TrackedRun:
    run_id: str
    run_name: str
    model_name: str
    model_uri: str
    artifact_uri: str


class MLflowTracker:
    """Reusable local MLflow tracking service."""

    def __init__(
        self,
        config: MLflowTrackingConfig,
    ) -> None:
        self.config = config

        mlflow.set_tracking_uri(
            config.tracking_uri
        )

        self.client = MlflowClient(
            tracking_uri=config.tracking_uri
        )

        self.experiment_id = (
            self._get_or_create_experiment()
        )

    def _get_or_create_experiment(
        self,
    ) -> str:
        existing = (
            self.client.get_experiment_by_name(
                self.config.experiment_name
            )
        )

        if existing is not None:
            return existing.experiment_id

        return self.client.create_experiment(
            name=self.config.experiment_name,
            artifact_location=(
                self.config.artifact_root
            ),
        )

    @contextmanager
    def parent_run(
        self,
        *,
        run_name: str,
        tags: dict[str, str] | None = None,
    ) -> Iterator[ActiveRun]:
        # Re-assert this tracker's own tracking URI before touching the
        # fluent API. mlflow.set_tracking_uri(...) is process-global state,
        # so if another MLflowTracker instance was constructed after this
        # one, its URI would otherwise silently "win" and every fluent call
        # below (start_run, log_params, log_model, ...) would write into the
        # wrong tracking store even though self.client is correctly bound.
        mlflow.set_tracking_uri(
            self.config.tracking_uri
        )

        with mlflow.start_run(
            experiment_id=self.experiment_id,
            run_name=run_name,
            tags=tags,
        ) as run:
            yield run

    def log_model_run(
        self,
        *,
        run_name: str,
        model_name: str,
        model: Pipeline,
        parameters: dict[str, object],
        metrics: dict[str, float],
        tags: dict[str, str],
        confusion_matrix: tuple[
            tuple[int, int],
            tuple[int, int],
        ],
        reproducibility_metadata: dict[
            str,
            object,
        ],
        input_example: pd.DataFrame,
        nested: bool = True,
    ) -> TrackedRun:
        # Same reasoning as in parent_run(): re-pin the tracking URI right
        # before starting the nested run, so this call is guaranteed to
        # write into *this* tracker's store regardless of what other
        # MLflowTracker instances have done to the global URI in the
        # meantime.
        mlflow.set_tracking_uri(
            self.config.tracking_uri
        )

        with mlflow.start_run(
            experiment_id=self.experiment_id,
            run_name=run_name,
            nested=nested,
            tags=tags,
        ) as run:
            mlflow.log_params(parameters)

            mlflow.log_metrics(metrics)

            mlflow.log_dict(
                {
                    "labels": [
                        ["TN", "FP"],
                        ["FN", "TP"],
                    ],
                    "matrix": [
                        list(
                            confusion_matrix[0]
                        ),
                        list(
                            confusion_matrix[1]
                        ),
                    ],
                },
                "evaluation/confusion_matrix.json",
            )

            mlflow.log_dict(
                reproducibility_metadata,
                "metadata/reproducibility.json",
            )

            mlflow.sklearn.log_model(
                model,
                name="model",
                input_example=input_example,
                serialization_format="cloudpickle",
            )

            return TrackedRun(
                run_id=run.info.run_id,
                run_name=run_name,
                model_name=model_name,
                model_uri=(
                    f"runs:/{run.info.run_id}/model"
                ),
                artifact_uri=(
                    run.info.artifact_uri
                ),
            )

    def search_child_runs(
        self,
        *,
        parent_run_id: str,
    ) -> list:
        return list(
            self.client.search_runs(
                experiment_ids=[
                    self.experiment_id
                ],
                filter_string=(
                    "tags.`mlflow.parentRunId` = "
                    f"'{parent_run_id}'"
                ),
                order_by=[
                    (
                        "metrics.average_precision "
                        "DESC"
                    )
                ],
            )
        )