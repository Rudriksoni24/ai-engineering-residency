from dataclasses import dataclass


@dataclass(frozen=True)
class IngestionResult:
    entity_count: int
    relationship_count: int


@dataclass(frozen=True)
class BankingAnswer:
    answer: str
    seed_entity_ids: list[str]
    retrieved_entity_count: int
    retrieved_relationship_count: int
    graph_context: str