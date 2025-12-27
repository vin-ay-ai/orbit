"""
STIX schema definitions

Schema validation for STIX-formatted objects and relationships.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .base import BaseNode, BaseEdge, ValidationError

# STIX ID pattern: <type>--<UUID>
STIX_ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]+--[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

# Common STIX object types in ATT&CK
ATTACK_OBJECT_TYPES = {
    "attack-pattern",
    "campaign",
    "course-of-action",
    "identity",
    "intrusion-set",
    "malware",
    "marking-definition",
    "relationship",
    "tool",
    "x-mitre-data-component",
    "x-mitre-data-source",
    "x-mitre-matrix",
    "x-mitre-tactic",
}


@dataclass
class STIXObject(BaseNode):
    """
    STIX object schema.

    Represents STIX objects (nodes) with required fields.
    """

    created: str | None = None
    modified: str | None = None
    spec_version: str | None = None

    def validate(self) -> None:
        """
        Validate STIX object.

        Checks:
        - ID format (STIX pattern)
        - Type is known
        - Required fields present

        Raises:
            ValidationError: If validation fails
        """
        super().validate()

        # Validate STIX ID format
        if not STIX_ID_PATTERN.match(self.id):
            raise ValidationError(
                f"Invalid STIX ID format: {self.id}. "
                f"Expected pattern: <type>--<uuid>"
            )

        # Extract type from ID and verify consistency
        id_type = self.id.split("--")[0]
        if id_type != self.type:
            raise ValidationError(
                f"STIX ID type mismatch: ID has '{id_type}', "
                f"but type field is '{self.type}'"
            )

        # Validate type is known (for ATT&CK)
        # Note: This is ATT&CK-specific and may need generalization
        if self.type not in ATTACK_OBJECT_TYPES:
            raise ValidationError(
                f"Unknown STIX type: {self.type}. "
                f"Known types: {', '.join(sorted(ATTACK_OBJECT_TYPES))}"
            )


@dataclass
class STIXRelationship(BaseEdge):
    """
    STIX relationship schema.

    Represents STIX relationships (edges) with validation.
    """

    id: str | None = None
    type: str = "relationship"

    def validate(self) -> None:
        """
        Validate STIX relationship.

        Checks:
        - Base edge validation
        - Type is 'relationship'
        - Source/target refs are valid STIX IDs

        Raises:
            ValidationError: If validation fails
        """
        super().validate()

        # Type must be 'relationship'
        if self.type != "relationship":
            raise ValidationError(
                f"STIX relationship type must be 'relationship', "
                f"got '{self.type}'"
            )

        # Validate source/target are STIX IDs
        if not STIX_ID_PATTERN.match(self.source_ref):
            raise ValidationError(
                f"Invalid source_ref STIX ID: {self.source_ref}"
            )

        if not STIX_ID_PATTERN.match(self.target_ref):
            raise ValidationError(
                f"Invalid target_ref STIX ID: {self.target_ref}"
            )

        # relationship_type should not be empty (checked in base)
        # Additional relationship type validation could be added here


def validate_stix_object(obj: dict[str, Any]) -> STIXObject | STIXRelationship:
    """
    Validate raw STIX object and return typed instance.

    Args:
        obj: Raw STIX object dictionary

    Returns:
        Validated STIXObject or STIXRelationship

    Raises:
        ValidationError: If validation fails
    """
    if "type" not in obj:
        raise ValidationError("STIX object missing 'type' field")

    if "id" not in obj:
        raise ValidationError("STIX object missing 'id' field")

    # Relationship vs Object
    if obj["type"] == "relationship":
        rel = STIXRelationship(
            source_ref=obj.get("source_ref", ""),
            target_ref=obj.get("target_ref", ""),
            relationship_type=obj.get("relationship_type", ""),
            id=obj.get("id"),
        )
        rel.validate()
        return rel
    else:
        node = STIXObject(
            id=obj["id"],
            type=obj["type"],
            created=obj.get("created"),
            modified=obj.get("modified"),
            spec_version=obj.get("spec_version"),
        )
        node.validate()
        return node
