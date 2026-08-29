import pytest

from graphrag.extraction.contracts import (
    ExtractedEntity,
    ExtractedRelationship,
    KnowledgeExtractionResult,
)


def test_extraction_result_counts():
    result = KnowledgeExtractionResult(
        entities=[
            ExtractedEntity(
                name="Ravi Sharma",
                entity_type="customer",
            ),
        ],
        relationships=[],
    )

    assert result.entity_count == 1
    assert result.relationship_count == 0


def test_extracted_entity_requires_name():
    with pytest.raises(
        ValueError,
        match="entity name cannot be empty",
    ):
        ExtractedEntity(
            name="",
            entity_type="customer",
        )


def test_extracted_relationship_requires_type():
    with pytest.raises(
        ValueError,
        match=(
            "relationship_type cannot "
            "be empty"
        ),
    ):
        ExtractedRelationship(
            source_name="Ravi",
            target_name="ACC001",
            relationship_type="",
        )