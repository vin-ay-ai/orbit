"""
Tests for source adapters
"""

import json
import pytest
from pathlib import Path

from orbit.adapters import get_adapter, AttackAdapter
from orbit.adapters.base import SourceAdapter


class TestAttackAdapter:
    """Tests for ATT&CK adapter."""

    def test_fetch_loads_stix_bundle(self, tmp_path):
        """Test that fetch loads STIX bundle from file."""
        # Arrange: Create test fixture
        bundle_data = {
            "type": "bundle",
            "id": "bundle--test-123",
            "objects": [
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--test-001",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                }
            ],
        }
        bundle_path = tmp_path / "test_bundle.json"
        bundle_path.write_text(json.dumps(bundle_data))

        adapter = AttackAdapter()

        # Act
        result = adapter.fetch(bundle_path)

        # Assert
        assert result["type"] == "bundle"
        assert "objects" in result
        assert len(result["objects"]) == 1

    def test_fetch_raises_on_missing_file(self):
        """Test that fetch raises FileNotFoundError for missing files."""
        adapter = AttackAdapter()
        missing_path = Path("/nonexistent/file.json")

        with pytest.raises(FileNotFoundError):
            adapter.fetch(missing_path)

    def test_normalize_extracts_objects(self):
        """Test that normalize extracts objects from bundle."""
        # Arrange
        bundle = {
            "type": "bundle",
            "objects": [
                {"id": "obj-1", "type": "attack-pattern"},
                {"id": "obj-2", "type": "malware"},
            ],
        }
        adapter = AttackAdapter()

        # Act
        result = adapter.normalize(bundle)

        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "obj-1"
        assert result[1]["id"] == "obj-2"

    def test_normalize_raises_on_invalid_bundle(self):
        """Test that normalize raises error for invalid bundle."""
        adapter = AttackAdapter()
        invalid_bundle = {"type": "bundle"}  # Missing 'objects'

        with pytest.raises(ValueError, match="missing 'objects' field"):
            adapter.normalize(invalid_bundle)

    def test_source_name(self):
        """Test that source_name returns 'attack'."""
        adapter = AttackAdapter()
        assert adapter.source_name == "attack"

    def test_determinism(self, tmp_path):
        """Test that adapter produces deterministic outputs."""
        # Arrange
        bundle_data = {
            "type": "bundle",
            "id": "bundle--test",
            "objects": [{"id": "obj-1", "type": "attack-pattern"}],
        }
        bundle_path = tmp_path / "test.json"
        bundle_path.write_text(json.dumps(bundle_data))

        adapter = AttackAdapter()

        # Act: Run twice
        result1 = adapter.normalize(adapter.fetch(bundle_path))
        result2 = adapter.normalize(adapter.fetch(bundle_path))

        # Assert: Results are identical
        assert result1 == result2


class TestAdapterRegistry:
    """Tests for adapter registry and get_adapter."""

    def test_get_adapter_returns_attack_adapter(self):
        """Test that get_adapter returns AttackAdapter for 'attack'."""
        adapter = get_adapter("attack")
        assert isinstance(adapter, AttackAdapter)

    def test_get_adapter_raises_on_unknown_source(self):
        """Test that get_adapter raises ValueError for unknown source."""
        with pytest.raises(ValueError, match="Unknown source"):
            get_adapter("unknown_source")

    def test_get_adapter_lists_available_sources(self):
        """Test that error message lists available sources."""
        with pytest.raises(ValueError, match="Available:"):
            get_adapter("invalid")
