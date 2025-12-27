"""
Base adapter interface

Defines contract for all source adapters.
"""

from pathlib import Path
from typing import Any, Protocol

# Type alias for raw data from source
RawData = dict[str, Any] | list[dict[str, Any]]


class SourceAdapter(Protocol):
    """
    Protocol for source adapters.

    Adapters isolate source-specific logic and provide uniform interface
    for ingestion pipeline.

    Responsibilities:
    - Fetch or load raw data from source
    - Normalize source format to internal representation
    - Handle source-specific quirks

    NOT responsible for:
    - Data validation (handled by schema layer)
    - Persistence (handled by ingestion pipeline)
    """

    def fetch(self, data_path: Path) -> RawData:
        """
        Fetch raw data from source.

        Args:
            data_path: Path to source data file or directory

        Returns:
            Raw data in source format

        Raises:
            FileNotFoundError: If data_path doesn't exist
            IOError: If data cannot be read
        """
        ...

    def normalize(self, raw: RawData) -> list[dict[str, Any]]:
        """
        Normalize raw data to internal representation.

        Converts source-specific format to standardized structure
        without validation (validation happens in schema layer).

        Args:
            raw: Raw data from fetch()

        Returns:
            List of normalized objects

        Note:
            Output is NOT validated - validation is centralized
            in schema layer.
        """
        ...

    @property
    def source_name(self) -> str:
        """
        Canonical source identifier.

        Returns:
            Source name (e.g., 'attack', 'd3fend')
        """
        ...
