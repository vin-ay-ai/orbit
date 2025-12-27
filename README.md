# Orbit

Unified ATT&CK and D3FEND knowledge graph ingestion pipeline for building structured, queryable threat intelligence knowledge graphs.

## Overview

Orbit is a clean, testable ingestion pipeline designed to transform STIX-formatted threat intelligence (ATT&CK, D3FEND) into a Neo4j knowledge graph. The project emphasizes schema clarity, reproducible runs, and maintainable architecture.

## Status

**Early development** - Structure-first rebuild phase.

Currently implemented:
- STIX bundle loader
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
├── src/orbit/           # Core package
│   ├── __init__.py
│   └── loaders.py       # STIX bundle loading functionality
├── data/                # STIX data files
│   └── enterprise-attack.json
├── ATT&CK STIX Analysis Workflow (Conceptual).ipynb  # Analysis guide
├── requirements.txt     # Python dependencies
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

## Goals

Build a clean, testable ingestion pipeline with:
- **Clear schema boundaries**: Well-defined data models and validation
- **Reproducible runs**: Deterministic pipeline execution
- **Single entrypoint**: Unified interface for ingestion operations
- **Testability**: Comprehensive test coverage
- **Extensibility**: Support for multiple threat intelligence sources (ATT&CK, D3FEND)

## Development

### Running Tests

```bash
pytest
```

### Project Principles

1. **Structure-first**: Define schema and validation before implementation
2. **Explicit over implicit**: Clear data flow and transformations
3. **Testable components**: Small, focused functions with clear contracts
4. **Documentation**: Code and workflow documentation in parallel

## Roadmap

- [ ] Complete STIX object type taxonomy
- [ ] Implement relationship extraction and validation
- [ ] Neo4j ingestion pipeline
- [ ] D3FEND integration
- [ ] Schema versioning and migration
- [ ] CLI interface
- [ ] Comprehensive test suite

## Contributing

This project is in early development. Design decisions and architecture are still being established.

## License

See LICENSE file for details.