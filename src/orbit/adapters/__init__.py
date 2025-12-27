"""
Source Adapters

Pluggable adapters for different threat intelligence sources.
Isolate source-specific logic from core ingestion pipeline.
"""

from .base import SourceAdapter, RawData
from .attack import AttackAdapter
from .d3fend import D3FENDAdapter

ADAPTERS = {
    "attack": AttackAdapter,
    "d3fend": D3FENDAdapter,
}


def get_adapter(source: str, **kwargs) -> SourceAdapter:
    """
    Get adapter instance for source.

    Args:
        source: Source identifier ('attack', 'd3fend', etc.)
        **kwargs: Adapter-specific configuration

    Returns:
        SourceAdapter instance

    Raises:
        ValueError: If source is unknown
    """
    if source not in ADAPTERS:
        available = ", ".join(ADAPTERS.keys())
        raise ValueError(f"Unknown source: {source}. Available: {available}")

    adapter_class = ADAPTERS[source]
    return adapter_class(**kwargs)


__all__ = [
    "SourceAdapter",
    "RawData",
    "AttackAdapter",
    "D3FENDAdapter",
    "get_adapter",
    "ADAPTERS",
]
