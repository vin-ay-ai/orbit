"""
ATT&CK STIX Adapter

Handles ingestion of MITRE ATT&CK data in STIX format.
"""

import json
from pathlib import Path
from typing import Any


class AttackAdapter:
    """
    Adapter for ATT&CK STIX bundles.

    Loads STIX-formatted ATT&CK data and normalizes to internal
    representation.
    """

    def fetch(self, data_path: Path) -> dict[str, Any]:
        """
        Load ATT&CK STIX bundle from file.

        Args:
            data_path: Path to STIX bundle JSON file

        Returns:
            Raw STIX bundle

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        if not data_path.exists():
            raise FileNotFoundError(f"ATT&CK data not found: {data_path}")

        with data_path.open(encoding="utf-8") as f:
            return json.load(f)

    def normalize(self, raw: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract STIX objects from bundle.

        ATT&CK STIX bundles have structure:
        {
            "type": "bundle",
            "id": "bundle--...",
            "objects": [...]
        }

        Args:
            raw: Raw STIX bundle from fetch()

        Returns:
            List of STIX objects (unvalidated)

        Note:
            Returns objects as-is without validation.
            Validation happens in schema layer.
        """
        if "objects" not in raw:
            raise ValueError("Invalid STIX bundle: missing 'objects' field")

        return raw["objects"]

    @property
    def source_name(self) -> str:
        return "attack"
