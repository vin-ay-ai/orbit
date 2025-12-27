# Orbit

Unified ATT&CK and D3FEND knowledge graph ingestion pipeline for building structured, queryable threat intelligence knowledge graphs.

## Overview

ORBIT.CyberOntology is an open-source project from ORBIT-AI.ORG that builds a cybersecurity knowledge graph connecting MITRE ATT&CK, MITRE D3FEND, and NIST Cybersecurity Framework (CSF 2.0), by leveraging existing ontologies and eriching them to create a unified, machine-readable model of cyber threats, defenses, and controls — a foundation for operational risk and resilience intelligence.

## Current Phase: Foundation Phase

**Status**: In Development

**Phase Goal**: Establish deterministic ingestion architecture with clear schema boundaries, reproducible runs, and extensibility for multiple threat intelligence sources.

### Phase Objectives

1. **Single Ingestion Entrypoint**: Clear, documented interface for all data ingestion
2. **Schema & Validation**: Explicit data models with validation at ingestion time
3. **Deterministic Execution**: Reproducible runs with identical inputs → identical outputs
4. **Testability**: Comprehensive test coverage with offline execution
5. **Extensibility**: Pluggable adapters for ATT&CK, D3FEND, and future sources

Currently implemented:
- STIX bundle loader foundation
- ATT&CK structural analysis framework
- Conceptual workflow documentation

## Features

- **STIX Bundle Loading**: Parse and load STIX-formatted threat intelligence data
- **Schema Analysis**: Identify and validate ATT&CK STIX structural layers (objects, relationships, embedded edges)
- **Knowledge Graph Ready**: Designed for Neo4j ingestion with clear schema boundaries
- **Reproducible Pipeline**: Single entrypoint architecture for consistent results

## Project Structure

```
orbit/
├── src/orbit/                   # Core package
│   ├── __init__.py
│   ├── loaders.py               # STIX bundle loading (legacy)
│   ├── ingestion/               # Core ingestion orchestration
│   │   ├── __init__.py
│   │   └── pipeline.py          # Single ingestion entrypoint
│   ├── adapters/                # Source-specific adapters
│   │   ├── __init__.py
│   │   ├── base.py              # Adapter interface
│   │   ├── attack.py            # ATT&CK adapter
│   │   └── d3fend.py            # D3FEND adapter
│   └── schemas/                 # Data models and validation
│       ├── __init__.py
│       ├── base.py              # Base schema definitions
│       └── stix.py              # STIX-specific schemas
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── fixtures/                # Deterministic test data
│   ├── test_ingestion.py
│   ├── test_adapters.py
│   └── test_schemas.py
├── data/                        # Source data files
│   └── enterprise-attack.json
├── playground/                  # Experimentation workspace
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md          # System architecture
│   └── CONTRIBUTING.md          # Developer guide
├── ATT&CK STIX Analysis Workflow (Conceptual).ipynb
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd orbit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.10+
- Neo4j 5.0+
- See `requirements.txt` for full dependency list:
  - `neo4j>=5.0.0`
  - `pytest>=7.0.0`
  - `requests>=2.31.0`
  - `pyld` (for JSON-LD processing)

## Usage

### Loading STIX Bundles

```python
from pathlib import Path
from orbit.loaders import load_stix_bundle

# Load ATT&CK STIX data
bundle_path = Path("data/enterprise-attack.json")
stix_objects = load_stix_bundle(bundle_path)

print(f"Loaded {len(stix_objects)} STIX objects")
```

### ATT&CK Analysis Workflow

See `ATT&CK STIX Analysis Workflow (Conceptual).ipynb` for a comprehensive guide to:
- Identifying ATT&CK structural layers (objects, relationships, embedded edges)
- Extracting schema information from STIX data
- Understanding technique/sub-technique hierarchies
- Handling lifecycle states (revoked, deprecated)
- Mapping STIX IDs to ATT&CK IDs

## Architectural Principles

Orbit follows these core principles to ensure reliability and maintainability:

1. **Schemas are contracts, not suggestions**: All data models are explicitly defined and enforced
2. **Relationships are validated, not assumed**: Schema validation at ingestion time
3. **Reproducibility > convenience**: Identical inputs always produce identical outputs
4. **Adapters isolate volatility**: Source-specific logic is encapsulated in adapters
5. **No silent coercion or lossy normalization**: Data transformation is explicit and traceable

## Development

### Running Tests

```bash
pytest
```

### Project Structure Principles

1. **Clear separation of concerns**:
   - `adapters/` - Source-specific ingestion logic (ATT&CK, D3FEND)
   - `schemas/` - Data models and validation contracts
   - `ingestion/` - Core orchestration and entrypoint
   - `tests/` - Deterministic, offline-executable test suite

2. **Deterministic execution**: Tests use pinned fixtures, no live external data

3. **Extensibility**: New sources added via adapter interface without core logic changes

## Foundation Phase Roadmap

### Phase Deliverables

- [ ] **Ingestion Module**: Single public entrypoint with documented interface
- [ ] **Schema Definitions**: Explicit data models for all ingested entities
- [ ] **Adapter Interface**: Pluggable adapter system for ATT&CK and D3FEND
- [ ] **Validation Layer**: Schema validation with clear failure modes
- [ ] **Test Suite**: Deterministic, offline-executable tests for all components
- [ ] **Developer Documentation**: Guide for adding new sources and running ingestion

### Success Criteria (Phase Exit Conditions)

The Foundation Phase is complete when:

- ✅ Fresh clone can ingest supported sources with one command
- ✅ Same inputs produce byte-identical outputs
- ✅ Invalid data fails loudly and predictably
- ✅ Adding new source doesn't require modifying core ingestion logic
- ✅ Tests run offline and pass deterministically

### Explicit Non-Goals (Out of Scope)

- Graph construction or reasoning logic
- Query interfaces or APIs
- Visualization or analytics
- Performance optimization beyond correctness
- Automated enrichment or inference
- Cross-source semantic reconciliation

## Contributing

This project is in early development. Design decisions and architecture are still being established.

## License

See LICENSE file for details.
