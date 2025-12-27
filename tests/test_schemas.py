"""
Tests for schema validation
"""

import pytest

from orbit.schemas import (
    BaseNode,
    BaseEdge,
    ValidationError,
    STIXObject,
    STIXRelationship,
)
from orbit.schemas.stix import validate_stix_object


class TestBaseNode:
    """Tests for BaseNode validation."""

    def test_valid_node(self):
        """Test that valid node passes validation."""
        node = BaseNode(id="test-001", type="test-type")
        node.validate()  # Should not raise

    def test_empty_id_raises(self):
        """Test that empty ID raises ValidationError."""
        node = BaseNode(id="", type="test-type")
        with pytest.raises(ValidationError, match="ID cannot be empty"):
            node.validate()

    def test_empty_type_raises(self):
        """Test that empty type raises ValidationError."""
        node = BaseNode(id="test-001", type="")
        with pytest.raises(ValidationError, match="type cannot be empty"):
            node.validate()


class TestBaseEdge:
    """Tests for BaseEdge validation."""

    def test_valid_edge(self):
        """Test that valid edge passes validation."""
        edge = BaseEdge(
            source_ref="src-001",
            target_ref="tgt-001",
            relationship_type="uses",
        )
        edge.validate()  # Should not raise

    def test_empty_source_raises(self):
        """Test that empty source_ref raises ValidationError."""
        edge = BaseEdge(
            source_ref="", target_ref="tgt-001", relationship_type="uses"
        )
        with pytest.raises(ValidationError, match="source_ref cannot be empty"):
            edge.validate()

    def test_empty_target_raises(self):
        """Test that empty target_ref raises ValidationError."""
        edge = BaseEdge(
            source_ref="src-001", target_ref="", relationship_type="uses"
        )
        with pytest.raises(ValidationError, match="target_ref cannot be empty"):
            edge.validate()

    def test_self_reference_raises(self):
        """Test that self-referential edge raises ValidationError."""
        edge = BaseEdge(
            source_ref="node-001",
            target_ref="node-001",
            relationship_type="uses",
        )
        with pytest.raises(ValidationError, match="Self-referential"):
            edge.validate()


class TestSTIXObject:
    """Tests for STIX object validation."""

    def test_valid_stix_object(self):
        """Test that valid STIX object passes validation."""
        obj = STIXObject(
            id="attack-pattern--12345678-1234-1234-1234-123456789abc",
            type="attack-pattern",
            created="2023-01-01T00:00:00.000Z",
        )
        obj.validate()  # Should not raise

    def test_invalid_stix_id_format_raises(self):
        """Test that invalid STIX ID format raises ValidationError."""
        obj = STIXObject(id="invalid-id", type="attack-pattern")
        with pytest.raises(ValidationError, match="Invalid STIX ID format"):
            obj.validate()

    def test_id_type_mismatch_raises(self):
        """Test that ID/type mismatch raises ValidationError."""
        obj = STIXObject(
            id="attack-pattern--12345678-1234-1234-1234-123456789abc",
            type="malware",  # Doesn't match ID type
        )
        with pytest.raises(ValidationError, match="type mismatch"):
            obj.validate()

    def test_unknown_type_raises(self):
        """Test that unknown STIX type raises ValidationError."""
        obj = STIXObject(
            id="unknown-type--12345678-1234-1234-1234-123456789abc",
            type="unknown-type",
        )
        with pytest.raises(ValidationError, match="Unknown STIX type"):
            obj.validate()


class TestSTIXRelationship:
    """Tests for STIX relationship validation."""

    def test_valid_stix_relationship(self):
        """Test that valid STIX relationship passes validation."""
        rel = STIXRelationship(
            source_ref="attack-pattern--12345678-1234-1234-1234-123456789abc",
            target_ref="malware--87654321-4321-4321-4321-cba987654321",
            relationship_type="uses",
        )
        rel.validate()  # Should not raise

    def test_invalid_source_ref_raises(self):
        """Test that invalid source_ref raises ValidationError."""
        rel = STIXRelationship(
            source_ref="invalid-id",
            target_ref="malware--87654321-4321-4321-4321-cba987654321",
            relationship_type="uses",
        )
        with pytest.raises(ValidationError, match="Invalid source_ref"):
            rel.validate()

    def test_invalid_target_ref_raises(self):
        """Test that invalid target_ref raises ValidationError."""
        rel = STIXRelationship(
            source_ref="attack-pattern--12345678-1234-1234-1234-123456789abc",
            target_ref="invalid-id",
            relationship_type="uses",
        )
        with pytest.raises(ValidationError, match="Invalid target_ref"):
            rel.validate()


class TestValidateSTIXObject:
    """Tests for validate_stix_object function."""

    def test_validates_stix_object(self):
        """Test validation of STIX object dictionary."""
        obj_dict = {
            "id": "attack-pattern--12345678-1234-1234-1234-123456789abc",
            "type": "attack-pattern",
            "created": "2023-01-01T00:00:00.000Z",
        }
        result = validate_stix_object(obj_dict)
        assert isinstance(result, STIXObject)
        assert result.id == obj_dict["id"]

    def test_validates_stix_relationship(self):
        """Test validation of STIX relationship dictionary."""
        rel_dict = {
            "id": "relationship--12345678-1234-1234-1234-123456789abc",
            "type": "relationship",
            "source_ref": "attack-pattern--aaaaaaaa-1234-1234-1234-123456789abc",
            "target_ref": "malware--bbbbbbbb-4321-4321-4321-cba987654321",
            "relationship_type": "uses",
        }
        result = validate_stix_object(rel_dict)
        assert isinstance(result, STIXRelationship)
        assert result.relationship_type == "uses"

    def test_missing_type_raises(self):
        """Test that missing 'type' field raises ValidationError."""
        obj_dict = {"id": "test-001"}
        with pytest.raises(ValidationError, match="missing 'type' field"):
            validate_stix_object(obj_dict)

    def test_missing_id_raises(self):
        """Test that missing 'id' field raises ValidationError."""
        obj_dict = {"type": "attack-pattern"}
        with pytest.raises(ValidationError, match="missing 'id' field"):
            validate_stix_object(obj_dict)
