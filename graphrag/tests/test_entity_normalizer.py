from graphrag.extraction.normalizer import (
    EntityNormalizer,
)


def test_normalizes_name():
    result = (
        EntityNormalizer.normalize_name(
            "  Ravi   Sharma  "
        )
    )

    assert result == "Ravi Sharma"


def test_normalizes_entity_type():
    result = (
        EntityNormalizer.normalize_type(
            "Payment System"
        )
    )

    assert result == "payment_system"


def test_creates_entity_id():
    result = (
        EntityNormalizer
        .create_entity_id(
            entity_type="Customer",
            name="Ravi Sharma",
        )
    )

    assert (
        result
        == "customer:ravi_sharma"
    )


def test_creates_relationship_id():
    result = (
        EntityNormalizer
        .create_relationship_id(
            source_id=(
                "customer:ravi_sharma"
            ),
            relationship_type="owns",
            target_id="account:acc001",
        )
    )

    assert result == (
        "customer:ravi_sharma:"
        "owns:"
        "account:acc001"
    )