import pytest

from graphrag.modeling.relationship import (
    Relationship,
)


def test_relationship_creation():
    relationship = Relationship(
        relationship_id="rel:001",
        source_id="customer:001",
        target_id="account:001",
        relationship_type="owns",
    )

    assert (
        relationship.source_id
        == "customer:001"
    )

    assert (
        relationship.target_id
        == "account:001"
    )

    assert (
        relationship.relationship_type
        == "owns"
    )


def test_relationship_requires_type():
    with pytest.raises(
        ValueError,
        match=(
            "relationship_type cannot "
            "be empty"
        ),
    ):
        Relationship(
            relationship_id="rel:001",
            source_id="customer:001",
            target_id="account:001",
            relationship_type="",
        )


def test_self_relationship_is_rejected():
    with pytest.raises(
        ValueError,
        match=(
            "self relationships are not "
            "allowed"
        ),
    ):
        Relationship(
            relationship_id="rel:001",
            source_id="customer:001",
            target_id="customer:001",
            relationship_type="owns",
        )