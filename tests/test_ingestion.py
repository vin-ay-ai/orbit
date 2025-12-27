"""
Tests for ingestion pipeline orchestration
"""

import pytest
from pathlib import Path

from orbit.ingestion import ingest, IngestConfig, IngestResult


class TestIngestConfig:
    """Tests for IngestConfig dataclass."""

    def test_config_creation(self):
        """Test creating ingestion configuration."""
        config = IngestConfig(
            source="attack",
            data_path=Path("/path/to/data.json"),
        )
        assert config.source == "attack"
        assert config.validate is True  # Default
        assert config.fail_on_invalid is True  # Default

    def test_config_with_custom_options(self):
        """Test configuration with custom options."""
        config = IngestConfig(
            source="attack",
            data_path=Path("/path/to/data.json"),
            validate=False,
            fail_on_invalid=False,
        )
        assert config.validate is False
        assert config.fail_on_invalid is False


class TestIngestResult:
    """Tests for IngestResult dataclass."""

    def test_result_is_valid_with_no_errors(self):
        """Test that result is valid when no errors."""
        result = IngestResult(objects=[{"id": "obj-1"}], errors=[])
        assert result.is_valid is True

    def test_result_is_invalid_with_errors(self):
        """Test that result is invalid when errors present."""
        result = IngestResult(objects=[], errors=["Error 1", "Error 2"])
        assert result.is_valid is False

    def test_object_count(self):
        """Test object_count property."""
        result = IngestResult(
            objects=[{"id": "obj-1"}, {"id": "obj-2"}], errors=[]
        )
        assert result.object_count == 2


class TestIngestPipeline:
    """Tests for ingest() function."""

    @pytest.mark.skip(reason="Pipeline not yet implemented")
    def test_ingest_with_attack_source(self, tmp_path):
        """Test ingestion with ATT&CK source."""
        # This test will be implemented when pipeline is complete
        config = IngestConfig(
            source="attack",
            data_path=tmp_path / "attack.json",
        )
        result = ingest(config)
        assert result.is_valid

    @pytest.mark.skip(reason="Pipeline not yet implemented")
    def test_ingest_determinism(self, tmp_path):
        """Test that ingestion produces deterministic results."""
        # This test ensures same input → same output
        # Will be implemented when pipeline is complete
        pass

    @pytest.mark.skip(reason="Pipeline not yet implemented")
    def test_ingest_validation_failure(self, tmp_path):
        """Test that invalid data fails validation."""
        # Will be implemented when pipeline is complete
        pass


# Placeholder for future integration tests
class TestEndToEndIngestion:
    """End-to-end ingestion tests."""

    @pytest.mark.skip(reason="Requires full pipeline implementation")
    def test_full_attack_ingestion(self):
        """Test complete ATT&CK ingestion workflow."""
        # Will test: fetch → normalize → validate → output
        pass
