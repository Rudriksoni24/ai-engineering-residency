from graphrag.extraction.extractor import (
    BankingKnowledgeExtractor,
)


def test_extracts_customer_and_account():
    extractor = (
        BankingKnowledgeExtractor()
    )

    result = extractor.extract(
        "Customer Ravi Sharma owns "
        "account ACC001."
    )

    entity_types = {
        entity.entity_type
        for entity in result.entities
    }

    assert "customer" in entity_types
    assert "account" in entity_types


def test_extracts_owns_relationship():
    extractor = (
        BankingKnowledgeExtractor()
    )

    result = extractor.extract(
        "Customer Ravi Sharma owns "
        "account ACC001."
    )

    assert (
        result.relationship_count
        == 1
    )

    relationship = (
        result.relationships[0]
    )

    assert (
        relationship
        .relationship_type
        == "owns"
    )

    assert (
        relationship.source_name
        == "Ravi Sharma"
    )

    assert (
        relationship.target_name
        == "ACC001"
    )


def test_extracts_transaction_relationship():
    extractor = (
        BankingKnowledgeExtractor()
    )

    result = extractor.extract(
        "Account ACC001 initiated "
        "transaction TXN9001."
    )

    assert (
        result.relationship_count
        == 1
    )

    relationship = (
        result.relationships[0]
    )

    assert (
        relationship
        .relationship_type
        == "initiated"
    )


def test_empty_text_returns_empty_result():
    extractor = (
        BankingKnowledgeExtractor()
    )

    result = extractor.extract("")

    assert result.entity_count == 0
    assert (
        result.relationship_count
        == 0
    )