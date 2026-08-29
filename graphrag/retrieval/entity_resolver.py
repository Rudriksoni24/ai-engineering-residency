import re

from graphrag.modeling.entity import Entity
from graphrag.storage.query_service import (
    GraphQueryService,
)


class EntityResolver:

    def __init__(
        self,
        query_service: GraphQueryService,
    ) -> None:
        self.query_service = query_service

    def resolve(
        self,
        query: str,
    ) -> list[Entity]:

        if not query.strip():
            return []

        resolved: dict[str, Entity] = {}

        query_lower = query.lower()

        for entity in (
            self.query_service
            .all_entities()
        ):
            name = entity.name.strip()

            if not name:
                continue

            pattern = (
                r"(?<!\w)"
                + re.escape(
                    name.lower()
                )
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                query_lower,
            ):
                resolved[
                    entity.entity_id
                ] = entity

        return sorted(
            resolved.values(),
            key=lambda entity: (
                entity.entity_id
            ),
        )