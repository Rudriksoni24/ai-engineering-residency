from graphrag.modeling.entity import Entity
from graphrag.retrieval.entity_resolver import (
    EntityResolver,
)
from graphrag.storage.query_service import (
    GraphQueryService,
)
from graphrag.storage.sqlite_store import (
    SQLiteGraphStore,
)


def create_resolver(
    tmp_path,
) -> EntityResolver:

    store = SQLiteGraphStore(
        tmp_path / "graph.db"
    )

    store.add_entity(
        Entity(
            entity_id="account:acc001",
            entity_type="account",
            name="ACC001",
        )
    )

    store.add_entity(
        Entity(
            entity_id="account:acc002",
            entity_type="account",
            name="ACC002",
        )
    )

    service = GraphQueryService(
        store
    )

    return EntityResolver(service)


def test_resolves_entity_from_query(
    tmp_path,
):
    resolver = create_resolver(
        tmp_path
    )

    entities = resolver.resolve(
        "What transactions were "
        "initiated by ACC001?"
    )

    assert len(entities) == 1

    assert (
        entities[0].entity_id
        == "account:acc001"
    )


def test_resolution_is_case_insensitive(
    tmp_path,
):
    resolver = create_resolver(
        tmp_path
    )

    entities = resolver.resolve(
        "show activity for acc001"
    )

    assert len(entities) == 1


def test_does_not_match_partial_name(
    tmp_path,
):
    resolver = create_resolver(
        tmp_path
    )

    entities = resolver.resolve(
        "Show account ACC"
    )

    assert entities == []


def test_empty_query_returns_no_entities(
    tmp_path,
):
    resolver = create_resolver(
        tmp_path
    )

    assert resolver.resolve("") == []