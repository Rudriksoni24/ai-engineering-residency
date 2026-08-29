from graphrag.extraction.contracts import (
    KnowledgeExtractionResult,
)
from graphrag.extraction.normalizer import (
    EntityNormalizer,
)
from graphrag.modeling.entity import Entity
from graphrag.modeling.graph import (
    KnowledgeGraph,
)
from graphrag.modeling.relationship import (
    Relationship,
)


class ExtractionGraphBuilder:

    def __init__(
        self,
        normalizer: EntityNormalizer
        | None = None,
    ) -> None:
        self.normalizer = (
            normalizer
            or EntityNormalizer()
        )

    def build(
        self,
        extraction: KnowledgeExtractionResult,
    ) -> KnowledgeGraph:

        graph = KnowledgeGraph()

        entity_ids_by_name: dict[
            str,
            str,
        ] = {}

        for extracted_entity in (
            extraction.entities
        ):

            entity_id = (
                self.normalizer
                .create_entity_id(
                    entity_type=(
                        extracted_entity
                        .entity_type
                    ),
                    name=(
                        extracted_entity
                        .name
                    ),
                )
            )

            entity = Entity(
                entity_id=entity_id,
                entity_type=(
                    extracted_entity
                    .entity_type
                ),
                name=(
                    self.normalizer
                    .normalize_name(
                        extracted_entity
                        .name
                    )
                ),
                properties=(
                    extracted_entity
                    .properties
                ),
            )

            if (
                graph.get_entity(
                    entity_id
                )
                is None
            ):
                graph.add_entity(
                    entity
                )

            entity_ids_by_name[
                extracted_entity
                .name.lower()
            ] = entity_id

        for extracted_relationship in (
            extraction.relationships
        ):

            source_id = (
                entity_ids_by_name.get(
                    extracted_relationship
                    .source_name
                    .lower()
                )
            )

            target_id = (
                entity_ids_by_name.get(
                    extracted_relationship
                    .target_name
                    .lower()
                )
            )

            if (
                source_id is None
                or target_id is None
            ):
                continue

            relationship_id = (
                self.normalizer
                .create_relationship_id(
                    source_id=source_id,
                    relationship_type=(
                        extracted_relationship
                        .relationship_type
                    ),
                    target_id=target_id,
                )
            )

            relationship = Relationship(
                relationship_id=(
                    relationship_id
                ),
                source_id=source_id,
                target_id=target_id,
                relationship_type=(
                    extracted_relationship
                    .relationship_type
                ),
                properties=(
                    extracted_relationship
                    .properties
                ),
            )

            graph.add_relationship(
                relationship
            )

        return graph