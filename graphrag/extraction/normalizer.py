import re


class EntityNormalizer:

    @staticmethod
    def normalize_name(
        value: str,
    ) -> str:
        return " ".join(
            value.strip().split()
        )

    @staticmethod
    def normalize_type(
        value: str,
    ) -> str:
        normalized = value.strip().lower()

        normalized = re.sub(
            r"[^a-z0-9]+",
            "_",
            normalized,
        )

        return normalized.strip("_")

    @classmethod
    def create_entity_id(
        cls,
        entity_type: str,
        name: str,
    ) -> str:

        normalized_type = (
            cls.normalize_type(
                entity_type
            )
        )

        normalized_name = (
            cls.normalize_name(name)
            .lower()
        )

        normalized_name = re.sub(
            r"[^a-z0-9]+",
            "_",
            normalized_name,
        )

        normalized_name = (
            normalized_name.strip("_")
        )

        return (
            f"{normalized_type}:"
            f"{normalized_name}"
        )

    @classmethod
    def create_relationship_id(
        cls,
        source_id: str,
        relationship_type: str,
        target_id: str,
    ) -> str:

        normalized_relationship = (
            cls.normalize_type(
                relationship_type
            )
        )

        return (
            f"{source_id}:"
            f"{normalized_relationship}:"
            f"{target_id}"
        )