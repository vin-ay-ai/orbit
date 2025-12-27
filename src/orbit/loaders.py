import json
from pathlib import Path
from typing import Any, Dict, List

from pyld import jsonld


def load_stix_bundle(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return json.load(f).get("objects", [])


