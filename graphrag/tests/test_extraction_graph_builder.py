from graphrag.extraction.contracts import (
    ExtractedEntity,
    ExtractedRelationship,
    KnowledgeExtractionResult,
)
from graphrag.extraction.graph_builder import (
    ExtractionGraphBuilder,
)


def test_builds_graph_from_extraction():
    extraction = (
        KnowledgeExtractionResult(
            entities=[
                ExtractedEntity(
                    name="Ravi Sharma",
                    entity_type=(
                        "customer"
                    ),
                ),
                ExtractedEntity(
                    name="ACC001",
                    entity_type="account",
                ),
            ],
            relationships=[
                ExtractedRelationship(
                    source_name=(
                        "Ravi Sharma"
                    ),
                    target_name="ACC001",
                    relationship_type=(
                        "owns"
                    ),
                ),
            ],
        )
    )

    builder = (
        ExtractionGraphBuilder()
    )

    graph = builder.build(
        extraction
    )

    assert len(graph.entities) == 2
    assert (
        len(graph.relationships)
        == 1
    )


def test_graph_uses_normalized_ids():
    extraction = (
        KnowledgeExtractionResult(
            entities=[
                ExtractedEntity(
                    name="Ravi Sharma",
                    entity_type=(
                        "Customer"
                    ),
                ),
            ],
            relationships=[],
        )
    )

    graph = (
        ExtractionGraphBuilder()
        .build(extraction)
    )

    entity = graph.get_entity(
        "customer:ravi_sharma"
    )

    assert entity is not None
    assert entity.name == "Ravi Sharma"