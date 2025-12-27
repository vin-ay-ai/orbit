"""
Schema Definitions and Validation

Explicit data models for all ingested entities.
Schemas are contracts - validation is enforced, not optional.
"""

from .base import BaseNode, BaseEdge, ValidationError
from .stix import STIXObject, STIXRelationship

__all__ = [
    "BaseNode",
    "BaseEdge",
    "ValidationError",
    "STIXObject",
    "STIXRelationship",
]
