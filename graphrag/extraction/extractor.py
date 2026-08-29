import re

from graphrag.extraction.contracts import (
    ExtractedEntity,
    ExtractedRelationship,
    KnowledgeExtractionResult,
)


class BankingKnowledgeExtractor:

    _ENTITY_PATTERNS = [
        (
            "customer",
            re.compile(
                r"customer\s+(.+?)(?=\s+owns\b)",
                re.IGNORECASE,
            ),
        ),
        (
            "account",
            re.compile(
                r"account\s+([A-Za-z0-9_-]+)",
                re.IGNORECASE,
            ),
        ),
        (
            "transaction",
            re.compile(
                r"transaction\s+([A-Za-z0-9_-]+)",
                re.IGNORECASE,
            ),
        ),
    ]

    def extract(
        self,
        text: str,
    ) -> KnowledgeExtractionResult:

        if not text.strip():
            return KnowledgeExtractionResult(
                entities=[],
                relationships=[],
            )

        entities = self._extract_entities(
            text
        )

        relationships = (
            self._extract_relationships(
                text=text,
                entities=entities,
            )
        )

        return KnowledgeExtractionResult(
            entities=entities,
            relationships=relationships,
        )

    def _extract_entities(
        self,
        text: str,
    ) -> list[ExtractedEntity]:

        entities: list[
            ExtractedEntity
        ] = []

        seen: set[
            tuple[str, str]
        ] = set()

        for (
            entity_type,
            pattern,
        ) in self._ENTITY_PATTERNS:

            for match in pattern.finditer(
                text
            ):
                name = (
                    match.group(1)
                    .strip()
                )

                key = (
                    entity_type,
                    name.lower(),
                )

                if key in seen:
                    continue

                seen.add(key)

                entities.append(
                    ExtractedEntity(
                        name=name,
                        entity_type=(
                            entity_type
                        ),
                    )
                )

        return entities

    def _extract_relationships(
        self,
        text: str,
        entities: list[
            ExtractedEntity
        ],
    ) -> list[
        ExtractedRelationship
    ]:

        relationships: list[
            ExtractedRelationship
        ] = []

        customer_names = [
            entity.name
            for entity in entities
            if entity.entity_type
            == "customer"
        ]

        account_names = [
            entity.name
            for entity in entities
            if entity.entity_type
            == "account"
        ]

        transaction_names = [
            entity.name
            for entity in entities
            if entity.entity_type
            == "transaction"
        ]

        text_lower = text.lower()

        if (
            customer_names
            and account_names
            and "owns" in text_lower
        ):
            relationships.append(
                ExtractedRelationship(
                    source_name=(
                        customer_names[0]
                    ),
                    target_name=(
                        account_names[0]
                    ),
                    relationship_type="owns",
                )
            )

        if (
            account_names
            and transaction_names
            and (
                "initiated" in text_lower
                or "initiates" in text_lower
            )
        ):
            relationships.append(
                ExtractedRelationship(
                    source_name=(
                        account_names[0]
                    ),
                    target_name=(
                        transaction_names[0]
                    ),
                    relationship_type=(
                        "initiated"
                    ),
                )
            )

        return relationships