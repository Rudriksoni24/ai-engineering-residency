from __future__ import annotations

from dataclasses import dataclass

import mlflow
import mlflow.sklearn
from mlflow import MlflowClient
from mlflow.entities.model_registry import ModelVersion
from mlflow.exceptions import MlflowException


@dataclass(frozen=True)
class RegisteredModelVersionInfo:
    model_name: str
    version: str
    source_run_id: str | None
    source_uri: str
    version_uri: str
    alias_uri: str | None
    aliases: tuple[str, ...]


class ModelRegistryService:
    """Manage local MLflow model lifecycle operations."""

    def __init__(
        self,
        *,
        tracking_uri: str,
    ) -> None:
        mlflow.set_tracking_uri(
            tracking_uri
        )

        self.client = MlflowClient(
            tracking_uri=tracking_uri
        )

    def ensure_registered_model(
        self,
        *,
        model_name: str,
        description: str | None = None,
    ) -> None:
        """Create the logical registered model when absent."""

        try:
            self.client.get_registered_model(
                model_name
            )
            return
        except MlflowException:
            pass

        self.client.create_registered_model(
            name=model_name,
            description=description,
            tags={
                "sprint": "8",
                "artifact": (
                    "Model Lifecycle Pipeline"
                ),
            },
        )

    def register_run_model(
        self,
        *,
        model_name: str,
        run_id: str,
        artifact_path: str = "model",
        description: str | None = None,
    ) -> RegisteredModelVersionInfo:
        """Register a logged run artifact as a new version."""

        self.ensure_registered_model(
            model_name=model_name,
            description=(
                "Sprint 8 fraud detection model"
            ),
        )

        run_model_uri = (
            f"runs:/{run_id}/{artifact_path}"
        )

        # MLflow 3.x logs models as first-class "Logged Model" entities
        # rather than files under the run's artifact directory, so the
        # legacy `runs:/{run_id}/{artifact_path}` convention above no
        # longer resolves to a real location in this installed version.
        # MLflowTracker.log_model_run stashes the real, correct model URI
        # (returned by mlflow.sklearn.log_model at logging time) as a
        # "model_uri" tag on the run — prefer that when it's present, and
        # only fall back to the deprecated runs:/ scheme for older runs
        # that predate this tag being set.
        run = self.client.get_run(run_id)
        tagged_model_uri = run.data.tags.get(
            "model_uri"
        )

        source = (
            tagged_model_uri
            if tagged_model_uri is not None
            else run_model_uri
        )

        model_version = (
            self.client.create_model_version(
                name=model_name,
                source=source,
                run_id=run_id,
                description=description,
                tags={
                    "source_run_id": run_id,
                    "lifecycle_status": (
                        "registered"
                    ),
                },
            )
        )

        return self._to_info(
            model_version
        )

    def list_versions(
        self,
        *,
        model_name: str,
    ) -> list[RegisteredModelVersionInfo]:
        """Return all registered versions for a model."""

        versions = (
            self.client.search_model_versions(
                filter_string=(
                    f"name='{model_name}'"
                )
            )
        )

        ordered = sorted(
            versions,
            key=lambda version: int(
                version.version
            ),
        )

        return [
            self._to_info(version)
            for version in ordered
        ]

    def assign_alias(
        self,
        *,
        model_name: str,
        version: str,
        alias: str,
    ) -> RegisteredModelVersionInfo:
        """Assign a lifecycle alias to a version."""

        self.client.set_registered_model_alias(
            name=model_name,
            alias=alias,
            version=version,
        )

        self.client.set_model_version_tag(
            name=model_name,
            version=version,
            key="lifecycle_status",
            value=alias,
        )

        updated = self.client.get_model_version(
            name=model_name,
            version=version,
        )

        return self._to_info(
            updated,
            alias=alias,
        )

    def mark_validation_status(
        self,
        *,
        model_name: str,
        version: str,
        status: str,
    ) -> None:
        """Store lifecycle metadata without performing validation."""

        self.client.set_model_version_tag(
            name=model_name,
            version=version,
            key="validation_status",
            value=status,
        )

    def get_version_by_alias(
        self,
        *,
        model_name: str,
        alias: str,
    ) -> RegisteredModelVersionInfo:
        model_version = (
            self.client.get_model_version_by_alias(
                name=model_name,
                alias=alias,
            )
        )

        return self._to_info(
            model_version,
            alias=alias,
        )

    def load_by_version(
        self,
        *,
        model_name: str,
        version: str,
    ):
        model_uri = (
            f"models:/{model_name}/{version}"
        )

        return mlflow.sklearn.load_model(
            model_uri
        )

    def load_by_alias(
        self,
        *,
        model_name: str,
        alias: str,
    ):
        model_uri = (
            f"models:/{model_name}@{alias}"
        )

        return mlflow.sklearn.load_model(
            model_uri
        )

    def inspect_lineage(
        self,
        *,
        model_name: str,
        version: str,
    ) -> dict[str, str | None]:
        model_version = (
            self.client.get_model_version(
                name=model_name,
                version=version,
            )
        )

        run_id = model_version.run_id

        result: dict[
            str,
            str | None,
        ] = {
            "model_name": (
                model_version.name
            ),
            "version": (
                model_version.version
            ),
            "source_run_id": run_id,
            "source_uri": (
                model_version.source
            ),
        }

        if run_id is None:
            result[
                "dataset_fingerprint"
            ] = None
            result[
                "model_type"
            ] = None
            return result

        run = self.client.get_run(
            run_id
        )

        result[
            "dataset_fingerprint"
        ] = run.data.params.get(
            "dataset_fingerprint"
        )

        result[
            "model_type"
        ] = run.data.params.get(
            "model_type"
        )

        return result

    def _to_info(
        self,
        model_version: ModelVersion,
        *,
        alias: str | None = None,
    ) -> RegisteredModelVersionInfo:
        aliases = tuple(
            model_version.aliases or []
        )

        alias_uri = None

        if alias is not None:
            alias_uri = (
                f"models:/"
                f"{model_version.name}"
                f"@{alias}"
            )

        return RegisteredModelVersionInfo(
            model_name=model_version.name,
            # Coerce explicitly: MLflow's ModelVersion class is type-hinted
            # as `version: str`, but this installed build was observed
            # returning a raw int from the backend store at runtime. Cast
            # here rather than trusting the declared type, since every
            # caller (tests, assign_alias, load_by_version, etc.) depends
            # on this being a string.
            version=str(
                model_version.version
            ),
            source_run_id=(
                model_version.run_id
            ),
            source_uri=(
                model_version.source
            ),
            version_uri=(
                f"models:/"
                f"{model_version.name}/"
                f"{model_version.version}"
            ),
            alias_uri=alias_uri,
            aliases=aliases,
        )