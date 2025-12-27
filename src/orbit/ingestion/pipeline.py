"""
Core ingestion pipeline

Provides single entrypoint for deterministic data ingestion.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class IngestConfig:
    """Configuration for ingestion operation."""

    source: str
    data_path: Path
    validate: bool = True
    fail_on_invalid: bool = True


@dataclass
class IngestResult:
    """Result of ingestion operation."""

    objects: list[dict[str, Any]]
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if ingestion completed without errors."""
        return len(self.errors) == 0

    @property
    def object_count(self) -> int:
        """Total number of successfully ingested objects."""
        return len(self.objects)


def ingest(config: IngestConfig) -> IngestResult:
    """
    Single ingestion entrypoint.

    Orchestrates: adapter fetch → normalize → validate → output

    Args:
        config: Ingestion configuration

    Returns:
        IngestResult with validated objects or errors

    Raises:
        ValueError: If source is unknown
        ValidationError: If validation fails and fail_on_invalid=True
    """
    # TODO: Implement full pipeline
    # 1. Get adapter for source
    # 2. Fetch raw data
    # 3. Normalize to internal representation
    # 4. Validate against schemas
    # 5. Return deterministic result

    return IngestResult(
        objects=[],
        errors=["Pipeline not yet implemented"],
        metadata={"source": config.source, "path": str(config.data_path)},
    )
