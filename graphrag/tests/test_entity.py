import pytest

from graphrag.modeling.entity import Entity


def test_entity_creation():
    entity = Entity(
        entity_id="customer:001",
        entity_type="customer",
        name="Ravi Sharma",
        properties={
            "segment": "premium",
        },
    )

    assert entity.entity_id == "customer:001"
    assert entity.entity_type == "customer"
    assert entity.name == "Ravi Sharma"
    assert (
        entity.properties["segment"]
        == "premium"
    )


def test_entity_requires_id():
    with pytest.raises(
        ValueError,
        match="entity_id cannot be empty",
    ):
        Entity(
            entity_id="",
            entity_type="customer",
            name="Ravi",
        )


def test_entity_requires_type():
    with pytest.raises(
        ValueError,
        match="entity_type cannot be empty",
    ):
        Entity(
            entity_id="customer:001",
            entity_type="",
            name="Ravi",
        )


def test_entity_requires_name():
    with pytest.raises(
        ValueError,
        match="name cannot be empty",
    ):
        Entity(
            entity_id="customer:001",
            entity_type="customer",
            name="",
        )