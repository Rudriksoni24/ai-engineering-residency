import json
import sqlite3
from pathlib import Path

from graphrag.modeling.entity import Entity
from graphrag.modeling.relationship import Relationship


class SQLiteGraphStore:

    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        self.database_path = str(
            database_path
        )

        self._initialize_schema()

    def _connect(
        self,
    ) -> sqlite3.Connection:

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = (
            sqlite3.Row
        )

        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    def _initialize_schema(
        self,
    ) -> None:

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    properties TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    properties TEXT NOT NULL,

                    FOREIGN KEY(source_id)
                        REFERENCES entities(entity_id),

                    FOREIGN KEY(target_id)
                        REFERENCES entities(entity_id)
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_entities_type
                ON entities(entity_type)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_relationship_source
                ON relationships(source_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_relationship_target
                ON relationships(target_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_relationship_type
                ON relationships(
                    relationship_type
                )
                """
            )

    def add_entity(
        self,
        entity: Entity,
    ) -> None:

        properties = json.dumps(
            entity.properties
        )

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO entities (
                    entity_id,
                    entity_type,
                    name,
                    properties
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(entity_id)
                DO UPDATE SET
                    entity_type = excluded.entity_type,
                    name = excluded.name,
                    properties = excluded.properties
                """,
                (
                    entity.entity_id,
                    entity.entity_type,
                    entity.name,
                    properties,
                ),
            )

    def get_entity(
        self,
        entity_id: str,
    ) -> Entity | None:

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    entity_id,
                    entity_type,
                    name,
                    properties
                FROM entities
                WHERE entity_id = ?
                """,
                (entity_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_entity(row)

    def get_entities(
        self,
    ) -> list[Entity]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    entity_id,
                    entity_type,
                    name,
                    properties
                FROM entities
                ORDER BY entity_id
                """
            ).fetchall()

        return [
            self._row_to_entity(row)
            for row in rows
        ]

    def get_entities_by_type(
        self,
        entity_type: str,
    ) -> list[Entity]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    entity_id,
                    entity_type,
                    name,
                    properties
                FROM entities
                WHERE entity_type = ?
                ORDER BY entity_id
                """,
                (entity_type,),
            ).fetchall()

        return [
            self._row_to_entity(row)
            for row in rows
        ]

    def find_entities_by_name(
        self,
        name: str,
    ) -> list[Entity]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    entity_id,
                    entity_type,
                    name,
                    properties
                FROM entities
                WHERE LOWER(name) = LOWER(?)
                ORDER BY entity_id
                """,
                (name.strip(),),
            ).fetchall()

        return [
            self._row_to_entity(row)
            for row in rows
        ]

    def add_relationship(
        self,
        relationship: Relationship,
    ) -> None:

        properties = json.dumps(
            relationship.properties
        )

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO relationships (
                    relationship_id,
                    source_id,
                    target_id,
                    relationship_type,
                    properties
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(relationship_id)
                DO UPDATE SET
                    source_id = excluded.source_id,
                    target_id = excluded.target_id,
                    relationship_type =
                        excluded.relationship_type,
                    properties =
                        excluded.properties
                """,
                (
                    relationship.relationship_id,
                    relationship.source_id,
                    relationship.target_id,
                    relationship.relationship_type,
                    properties,
                ),
            )

    def get_relationships(
        self,
    ) -> list[Relationship]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    relationship_id,
                    source_id,
                    target_id,
                    relationship_type,
                    properties
                FROM relationships
                ORDER BY relationship_id
                """
            ).fetchall()

        return [
            self._row_to_relationship(row)
            for row in rows
        ]

    def get_outgoing_relationships(
        self,
        entity_id: str,
    ) -> list[Relationship]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    relationship_id,
                    source_id,
                    target_id,
                    relationship_type,
                    properties
                FROM relationships
                WHERE source_id = ?
                ORDER BY relationship_id
                """,
                (entity_id,),
            ).fetchall()

        return [
            self._row_to_relationship(row)
            for row in rows
        ]

    def get_incoming_relationships(
        self,
        entity_id: str,
    ) -> list[Relationship]:

        with self._connect() as connection:

            rows = connection.execute(
                """
                SELECT
                    relationship_id,
                    source_id,
                    target_id,
                    relationship_type,
                    properties
                FROM relationships
                WHERE target_id = ?
                ORDER BY relationship_id
                """,
                (entity_id,),
            ).fetchall()

        return [
            self._row_to_relationship(row)
            for row in rows
        ]

    @staticmethod
    def _row_to_entity(
        row: sqlite3.Row,
    ) -> Entity:

        return Entity(
            entity_id=row["entity_id"],
            entity_type=row["entity_type"],
            name=row["name"],
            properties=json.loads(
                row["properties"]
            ),
        )

    @staticmethod
    def _row_to_relationship(
        row: sqlite3.Row,
    ) -> Relationship:

        return Relationship(
            relationship_id=(
                row["relationship_id"]
            ),
            source_id=row["source_id"],
            target_id=row["target_id"],
            relationship_type=(
                row["relationship_type"]
            ),
            properties=json.loads(
                row["properties"]
            ),
        )