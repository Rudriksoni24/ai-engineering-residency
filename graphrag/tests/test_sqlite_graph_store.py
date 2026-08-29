import pytest

from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import (
    Relationship,
)
from graphrag.storage.sqlite_store import (
    SQLiteGraphStore,
)


@pytest.fixture
def store(tmp_path):
    database_path = (
        tmp_path / "graph.db"
    )

    return SQLiteGraphStore(
        database_path
    )


def test_adds_and_reads_entity(
    store,
):
    entity = Entity(
        entity_id="customer:ravi_sharma",
        entity_type="customer",
        name="Ravi Sharma",
        properties={
            "segment": "premium",
        },
    )

    store.add_entity(entity)

    loaded = store.get_entity(
        "customer:ravi_sharma"
    )

    assert loaded is not None
    assert loaded == entity


def test_entity_properties_are_persisted(
    store,
):
    entity = Entity(
        entity_id="account:acc001",
        entity_type="account",
        name="ACC001",
        properties={
            "currency": "INR",
            "status": "active",
        },
    )

    store.add_entity(entity)

    loaded = store.get_entity(
        "account:acc001"
    )

    assert loaded is not None
    assert (
        loaded.properties["currency"]
        == "INR"
    )
    assert (
        loaded.properties["status"]
        == "active"
    )


def test_get_entities_by_type(
    store,
):
    store.add_entity(
        Entity(
            entity_id="customer:ravi",
            entity_type="customer",
            name="Ravi",
        )
    )

    store.add_entity(
        Entity(
            entity_id="account:acc001",
            entity_type="account",
            name="ACC001",
        )
    )

    customers = (
        store.get_entities_by_type(
            "customer"
        )
    )

    assert len(customers) == 1
    assert (
        customers[0].entity_id
        == "customer:ravi"
    )

def test_finds_entity_by_name(
    store,
):
    store.add_entity(
        Entity(
            entity_id="account:acc001",
            entity_type="account",
            name="ACC001",
        )
    )

    entities = (
        store.find_entities_by_name(
            "acc001"
        )
    )

    assert len(entities) == 1

    assert (
        entities[0].entity_id
        == "account:acc001"
    )


def test_adds_and_reads_relationship(
    store,
):
    customer = Entity(
        entity_id="customer:ravi",
        entity_type="customer",
        name="Ravi",
    )

    account = Entity(
        entity_id="account:acc001",
        entity_type="account",
        name="ACC001",
    )

    store.add_entity(customer)
    store.add_entity(account)

    relationship = Relationship(
        relationship_id=(
            "customer:ravi:"
            "owns:"
            "account:acc001"
        ),
        source_id="customer:ravi",
        target_id="account:acc001",
        relationship_type="owns",
    )

    store.add_relationship(
        relationship
    )

    relationships = (
        store.get_relationships()
    )

    assert len(relationships) == 1
    assert (
        relationships[0]
        == relationship
    )


def test_outgoing_relationships(
    store,
):
    store.add_entity(
        Entity(
            entity_id="customer:ravi",
            entity_type="customer",
            name="Ravi",
        )
    )

    store.add_entity(
        Entity(
            entity_id="account:acc001",
            entity_type="account",
            name="ACC001",
        )
    )

    store.add_relationship(
        Relationship(
            relationship_id="rel:001",
            source_id="customer:ravi",
            target_id="account:acc001",
            relationship_type="owns",
        )
    )

    relationships = (
        store
        .get_outgoing_relationships(
            "customer:ravi"
        )
    )

    assert len(relationships) == 1
    assert (
        relationships[0]
        .target_id
        == "account:acc001"
    )


def test_incoming_relationships(
    store,
):
    store.add_entity(
        Entity(
            entity_id="customer:ravi",
            entity_type="customer",
            name="Ravi",
        )
    )

    store.add_entity(
        Entity(
            entity_id="account:acc001",
            entity_type="account",
            name="ACC001",
        )
    )

    store.add_relationship(
        Relationship(
            relationship_id="rel:001",
            source_id="customer:ravi",
            target_id="account:acc001",
            relationship_type="owns",
        )
    )

    relationships = (
        store
        .get_incoming_relationships(
            "account:acc001"
        )
    )

    assert len(relationships) == 1
    assert (
        relationships[0]
        .source_id
        == "customer:ravi"
    )


def test_graph_persists_between_instances(
    tmp_path,
):
    database_path = (
        tmp_path / "graph.db"
    )

    first_store = SQLiteGraphStore(
        database_path
    )

    first_store.add_entity(
        Entity(
            entity_id="customer:ravi",
            entity_type="customer",
            name="Ravi",
        )
    )

    second_store = SQLiteGraphStore(
        database_path
    )

    loaded = second_store.get_entity(
        "customer:ravi"
    )

    assert loaded is not None
    assert loaded.name == "Ravi"