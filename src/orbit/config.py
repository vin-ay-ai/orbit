import os
from pathlib import Path
from typing import ClassVar, Set

from pydantic import BaseModel, field_validator


class IngestSettings(BaseModel):
    """
    Central configuration for the ingest pipeline.

    Settings are sourced from environment variables with sensible defaults so
    the package can run locally while remaining configurable in CI/CD.
    """
    DEFAULT_STIX_URL: ClassVar[str] = "https://github.com/mitre/cti/blob/master/enterprise-attack/enterprise-attack.json"
    DEFAULT_STIX_FILE: ClassVar[Path] = Path("attack-graph/stix-data/enterprise-attack.json")
    DEFAULT_D3FEND_JSONLD: ClassVar[Path] = Path("data/d3fend.json")

    stix_file: Path = DEFAULT_STIX_FILE
    d3fend_jsonld_path: Path = DEFAULT_D3FEND_JSONLD
    d3fend_ns: str = "http://d3fend.mitre.org/ontologies/d3fend.owl#"
    d3fend_tactic_names: Set[str] = {"Harden", "Detect", "Isolate", "Deceive", "Evict"}

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_pass: str = "Carpediem!23"
    neo4j_db: str = "unified"

    # LLM configuration for relationship validation
    use_llm_validation: bool = False
    llm_provider: str = "openai"  # openai or anthropic
    llm_model: str = "gpt-4o-mini"  # or claude-opus for Anthropic
    llm_api_key: str = ""
    llm_cache_enabled: bool = True

    # Cache control for data freshness
    force_refresh_data: bool = False  # Force reload all data from disk
    skip_llm_cache: bool = False      # Skip LLM cache (always call API for validation)
    force_reload_on_change: bool = True  # Force reload if data files are modified

    @field_validator("d3fend_tactic_names", mode="before")
    def _parse_tactics(cls, value):
        if isinstance(value, str):
            return {part.strip() for part in value.split(",") if part.strip()}
        return value

    @classmethod
    def from_env(cls) -> "IngestSettings":
        """
        Build a settings object by reading supported environment variables.
        """

        def _fetch(*names: str, default: str | Path | Set[str]):
            for name in names:
                value = os.getenv(name)
                if value:
                    return value
            return default

        return cls(
            stix_file=_fetch("UNIFIED_INGEST_STIX_FILE", "STIX_FILE", default=str(cls.DEFAULT_STIX_FILE)),
            d3fend_jsonld_path=_fetch(
                "UNIFIED_INGEST_D3FEND_JSONLD_PATH",
                "D3FEND_JSONLD_PATH",
                default=str(cls.DEFAULT_D3FEND_JSONLD),
            ),
            d3fend_ns=_fetch("UNIFIED_INGEST_D3FEND_NS", "D3FEND_NS", default="http://d3fend.mitre.org/ontologies/d3fend.owl#"),
            d3fend_tactic_names=_fetch(
                "UNIFIED_INGEST_D3FEND_TACTIC_NAMES",
                "D3FEND_TACTIC_NAMES",
                default={"Harden", "Detect", "Isolate", "Deceive", "Evict"},
            ),
            neo4j_uri=_fetch("UNIFIED_INGEST_NEO4J_URI", "NEO4J_URI", default="bolt://localhost:7687"),
            neo4j_user=_fetch("UNIFIED_INGEST_NEO4J_USER", "NEO4J_USER", default="neo4j"),
            neo4j_pass=_fetch("UNIFIED_INGEST_NEO4J_PASS", "NEO4J_PASS", default="Carpediem!23"),
            neo4j_db=_fetch("UNIFIED_INGEST_NEO4J_DB", "NEO4J_DB", default="unified"),
            use_llm_validation=os.getenv("UNIFIED_INGEST_USE_LLM_VALIDATION", "false").lower() == "true",
            llm_provider=_fetch("UNIFIED_INGEST_LLM_PROVIDER", "LLM_PROVIDER", default="openai"),
            llm_model=_fetch("UNIFIED_INGEST_LLM_MODEL", "LLM_MODEL", default="gpt-4o-mini"),
            llm_api_key=_fetch("UNIFIED_INGEST_LLM_API_KEY", "LLM_API_KEY", default=""),
            llm_cache_enabled=os.getenv("UNIFIED_INGEST_LLM_CACHE_ENABLED", "true").lower() == "true",
            force_refresh_data=os.getenv("UNIFIED_INGEST_FORCE_REFRESH_DATA", "false").lower() == "true",
            skip_llm_cache=os.getenv("UNIFIED_INGEST_SKIP_LLM_CACHE", "false").lower() == "true",
            force_reload_on_change=os.getenv("UNIFIED_INGEST_FORCE_RELOAD_ON_CHANGE", "true").lower() == "true",
        )


settings = IngestSettings.from_env()

# ========== FILE LOCATIONS ==========
STIX_FILE = settings.stix_file
D3FEND_JSONLD_PATH = settings.d3fend_jsonld_path

# ========== D3FEND ONTOLOGY ==========
D3FEND_NS = settings.d3fend_ns
D3FEND_ID_IRI = D3FEND_NS + "d3fend-id"
ENABLES_IRI = D3FEND_NS + "enables"
D3FEND_ARTIFACT_TYPE_IRI = D3FEND_NS + "DigitalArtifact"
D3FEND_DETECTS_IRI = D3FEND_NS + "detects"
D3FEND_DEPRIVES_IRI = D3FEND_NS + "deprives"
D3FEND_IMPLEMENTS_IRI = D3FEND_NS + "implements"
D3FEND_TACTIC_NAMES = set(settings.d3fend_tactic_names)


# ========== NEO4J CONNECTION ==========
NEO4J_URI = settings.neo4j_uri
NEO4J_USER = settings.neo4j_user
NEO4J_PASS = settings.neo4j_pass
NEO4J_DB = settings.neo4j_db  # unified graph database

# ========== LLM CONFIGURATION ==========
USE_LLM_VALIDATION = settings.use_llm_validation
LLM_PROVIDER = settings.llm_provider
LLM_MODEL = settings.llm_model
LLM_API_KEY = settings.llm_api_key
LLM_CACHE_ENABLED = settings.llm_cache_enabled

# ========== CACHE CONTROL ==========
FORCE_REFRESH_DATA = settings.force_refresh_data
SKIP_LLM_CACHE = settings.skip_llm_cache
FORCE_RELOAD_ON_CHANGE = settings.force_reload_on_change

__all__ = [
    "settings",
    "STIX_FILE",
    "D3FEND_JSONLD_PATH",
    "D3FEND_NS",
    "D3FEND_ID_IRI",
    "ENABLES_IRI",
    "D3FEND_ARTIFACT_TYPE_IRI",
    "D3FEND_DETECTS_IRI",
    "D3FEND_DEPRIVES_IRI",
    "D3FEND_IMPLEMENTS_IRI",
    "D3FEND_TACTIC_NAMES",
    "NEO4J_URI",
    "NEO4J_USER",
    "NEO4J_PASS",
    "NEO4J_DB",
    "USE_LLM_VALIDATION",
    "LLM_PROVIDER",
    "LLM_MODEL",
    "LLM_API_KEY",
    "LLM_CACHE_ENABLED",
    "FORCE_REFRESH_DATA",
    "SKIP_LLM_CACHE",
    "FORCE_RELOAD_ON_CHANGE",
]
