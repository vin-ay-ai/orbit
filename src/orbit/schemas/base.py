"""
Base schema definitions

Core abstractions for nodes, edges, and validation.
"""

from dataclasses import dataclass
from typing import Any


class ValidationError(Exception):
    """
    Raised when data fails schema validation.

    Validation errors must be explicit and actionable.
    """

    pass


@dataclass
class BaseNode:
    """
    Base class for node objects.

    All ingested entities that represent nodes in the knowledge graph
    should inherit from this class.
    """

    id: str
    type: str

    def validate(self) -> None:
        """
        Validate node against schema.

        Raises:
            ValidationError: If validation fails
        """
        if not self.id:
            raise ValidationError("Node ID cannot be empty")

        if not self.type:
            raise ValidationError("Node type cannot be empty")


@dataclass
class BaseEdge:
    """
    Base class for edge objects (relationships).

    All ingested relationships should inherit from this class.
    """

    source_ref: str
    target_ref: str
    relationship_type: str

    def validate(self) -> None:
        """
        Validate edge against schema.

        Raises:
            ValidationError: If validation fails
        """
        if not self.source_ref:
            raise ValidationError("Edge source_ref cannot be empty")

        if not self.target_ref:
            raise ValidationError("Edge target_ref cannot be empty")

        if not self.relationship_type:
            raise ValidationError("Edge relationship_type cannot be empty")

        if self.source_ref == self.target_ref:
            raise ValidationError(
                f"Self-referential edge not allowed: {self.source_ref}"
            )
