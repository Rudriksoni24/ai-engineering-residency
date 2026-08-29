import pytest

from graphrag.application.config import (
    BankingGraphConfig,
)
from graphrag.application.factory import (
    build_banking_graph_service,
)


def test_builds_banking_service(
    tmp_path,
):
    config = BankingGraphConfig(
        database_path=(
            tmp_path / "banking.db"
        ),
        model="test-model",
    )

    service = (
        build_banking_graph_service(
            config
        )
    )

    assert service is not None

    assert (
        service.entity_count()
        == 0
    )


def test_config_rejects_empty_model(
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match="model cannot be empty",
    ):
        BankingGraphConfig(
            database_path=(
                tmp_path / "banking.db"
            ),
            model="",
        )


def test_config_rejects_negative_depth(
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match=(
            "max_depth cannot "
            "be negative"
        ),
    ):
        BankingGraphConfig(
            database_path=(
                tmp_path / "banking.db"
            ),
            model="test-model",
            max_depth=-1,
        )


def test_config_rejects_zero_entity_limit(
    tmp_path,
):
    with pytest.raises(
        ValueError,
        match=(
            "max_entities must "
            "be at least 1"
        ),
    ):
        BankingGraphConfig(
            database_path=(
                tmp_path / "banking.db"
            ),
            model="test-model",
            max_entities=0,
        )