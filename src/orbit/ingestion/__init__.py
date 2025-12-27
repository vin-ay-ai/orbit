"""
Orbit Ingestion Module

Single entrypoint for all threat intelligence data ingestion.
Orchestrates adapter → validation → output flow.
"""

from .pipeline import ingest, IngestConfig, IngestResult

__all__ = ["ingest", "IngestConfig", "IngestResult"]
