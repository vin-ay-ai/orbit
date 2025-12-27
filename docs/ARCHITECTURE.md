# Orbit Architecture

## Foundation Phase — Deterministic Ingestion Architecture

### Purpose

Establish a clean, deterministic, and extensible ingestion pipeline that serves as the single, trustworthy entrypoint for all threat intelligence data entering the system.

This architecture eliminates ambiguity at the system boundary: what data is accepted, how it is validated, how it is reproduced, and how future sources are added without refactoring core logic.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      External Sources                        │
│  (ATT&CK STIX, D3FEND, Custom Threat Intelligence)          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Source Adapters                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ATT&CK       │  │ D3FEND       │  │ Custom       │      │
│  │ Adapter      │  │ Adapter      │  │ Adapter      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                  │               │
│         └─────────────────┴──────────────────┘               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Schema Validation Layer                         │
│  • Object type validation                                    │
│  • Relationship validation                                   │
│  • Field presence & type checking                            │
│  • Version compatibility checks                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           Ingestion Orchestration (Entrypoint)               │
│  • Deterministic execution                                   │
│  • Error handling & reporting                                │
│  • Reproducible outputs                                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Persistence-Ready Outputs                        │
│  (Validated, normalized data ready for graph ingestion)     │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Source Adapters (`src/orbit/adapters/`)

**Purpose**: Isolate source-specific ingestion logic

**Responsibilities**:
- Fetch or load raw data from source
- Convert source format to internal representation
- Handle source-specific quirks and edge cases
- No validation logic (delegated to schemas)

**Interface** (`adapters/base.py`):
```python
class SourceAdapter(Protocol):
    def fetch(self) -> RawData:
        """Fetch raw data from source"""
        ...

    def normalize(self, raw: RawData) -> list[dict]:
        """Convert to internal representation"""
        ...

    @property
    def source_name(self) -> str:
        """Canonical source identifier"""
        ...
```

**Implementations**:
- `attack.py` - ATT&CK STIX adapter
- `d3fend.py` - D3FEND adapter
- Future: CAPEC, CVE, custom sources

**Design Principles**:
- Adapters are **pluggable** - new sources added without modifying core logic
- Adapters **isolate volatility** - source changes don't affect validation or orchestration
- Adapters produce **unvalidated** outputs - validation is centralized

---

### 2. Schema Layer (`src/orbit/schemas/`)

**Purpose**: Define and enforce data contracts

**Responsibilities**:
- Define explicit data models for all entities
- Validate object types, relationships, fields
- Provide clear failure messages for invalid data
- Version compatibility checking

**Schema Types**:
- **Base schemas** (`base.py`): Core abstractions (Node, Edge, Bundle)
- **STIX schemas** (`stix.py`): STIX-specific object types and relationships
- **Validation rules**: Field presence, type checking, relationship constraints

**Validation Strategy**:
- **Fail loudly**: Invalid data raises explicit exceptions
- **No silent coercion**: No automatic type conversion or field mutation
- **Traceable failures**: Clear messages indicating what failed and why

**Example**:
```python
class STIXObject(BaseModel):
    id: str
    type: str
    created: datetime
    modified: datetime
    # ... additional fields with validation

    @validator('type')
    def validate_type(cls, v):
        if v not in ALLOWED_STIX_TYPES:
            raise ValueError(f"Invalid STIX type: {v}")
        return v
```

---

### 3. Ingestion Orchestration (`src/orbit/ingestion/`)

**Purpose**: Single entrypoint for all ingestion operations

**Responsibilities**:
- Coordinate adapter → validation → output flow
- Ensure deterministic execution
- Handle errors and produce clear reports
- Provide single public API for ingestion

**Key Module** (`pipeline.py`):
```python
def ingest(source: str, config: IngestConfig) -> IngestResult:
    """
    Single ingestion entrypoint

    Args:
        source: Source identifier ('attack', 'd3fend', etc.)
        config: Ingestion configuration (paths, options)

    Returns:
        IngestResult with validated objects or errors
    """
    # 1. Select adapter
    adapter = get_adapter(source)

    # 2. Fetch and normalize
    raw_data = adapter.fetch()
    normalized = adapter.normalize(raw_data)

    # 3. Validate
    validated = validate_objects(normalized)

    # 4. Return deterministic result
    return IngestResult(objects=validated, errors=[], metadata={...})
```

**Determinism Guarantees**:
- Same input files → same output objects (byte-identical)
- Stable ordering of objects and relationships
- Reproducible error messages
- No external state dependencies

---

## Architectural Principles

### 1. Schemas are contracts, not suggestions
- All data models explicitly defined
- Validation enforced at ingestion time
- No "soft" or optional validation modes

### 2. Relationships are validated, not assumed
- Relationship types validated against schema
- Source/target types checked for compatibility
- Invalid relationships rejected with clear errors

### 3. Reproducibility > convenience
- Deterministic execution prioritized over flexibility
- Same inputs always produce identical outputs
- No time-dependent or random behavior

### 4. Adapters isolate volatility
- Source-specific logic encapsulated in adapters
- Core ingestion logic independent of source changes
- New sources added via adapter interface only

### 5. No silent coercion or lossy normalization
- Data transformations are explicit
- No automatic type conversion
- Normalization steps documented and traceable

---

## Data Flow

### Happy Path

1. **Adapter Fetch**: Load raw data from source (file, API, etc.)
2. **Adapter Normalize**: Convert to internal representation
3. **Schema Validate**: Check types, fields, relationships
4. **Output Generation**: Produce persistence-ready objects
5. **Result Return**: Deliver validated data or errors

### Error Handling

**Invalid Object**:
- Schema validation fails
- Error logged with object ID, type, and failure reason
- Object excluded from output
- Ingestion continues for remaining objects

**Invalid Relationship**:
- Relationship type not in schema
- Source/target types incompatible
- Edge logged to errors, not included in output

**Partial Ingestion**:
- Not allowed - either all objects valid or ingestion fails
- Atomic operation guarantee

**Unsupported Version**:
- Schema version check fails
- Clear error message with supported versions
- Ingestion aborts

---

## Testing Strategy

### Principles

1. **Deterministic fixtures**: All test data version-controlled
2. **Offline execution**: No network calls during tests
3. **Comprehensive coverage**: Unit tests for adapters, schemas, orchestration

### Test Structure

```
tests/
├── fixtures/
│   ├── attack_sample.json       # Minimal ATT&CK bundle
│   ├── d3fend_sample.json       # Minimal D3FEND data
│   └── invalid_samples/         # Invalid data for error testing
├── test_adapters.py             # Adapter unit tests
├── test_schemas.py              # Schema validation tests
└── test_ingestion.py            # End-to-end orchestration tests
```

### Test Categories

**Adapter Tests**:
- Fetch from fixture files
- Normalize to expected format
- Handle source-specific edge cases

**Schema Tests**:
- Valid objects pass validation
- Invalid objects fail with clear errors
- Relationship type validation
- Field presence and type checking

**Ingestion Tests**:
- End-to-end ingestion from fixture
- Deterministic output verification
- Error handling and reporting
- Partial failure scenarios

---

## Extensibility

### Adding a New Source

1. **Create Adapter** (`src/orbit/adapters/newsource.py`):
   ```python
   class NewSourceAdapter(SourceAdapter):
       def fetch(self) -> RawData: ...
       def normalize(self, raw: RawData) -> list[dict]: ...
       @property
       def source_name(self) -> str:
           return "newsource"
   ```

2. **Register Adapter** (`src/orbit/adapters/__init__.py`):
   ```python
   ADAPTERS = {
       "attack": AttackAdapter,
       "d3fend": D3FENDAdapter,
       "newsource": NewSourceAdapter,
   }
   ```

3. **Add Schema** (if new object types):
   - Define models in `schemas/`
   - Add validation rules

4. **Create Fixtures**:
   - Add sample data to `tests/fixtures/`
   - Write adapter tests

5. **Test**:
   ```bash
   pytest tests/test_adapters.py::test_newsource_adapter
   ```

**No changes required to**:
- Core ingestion logic
- Existing adapters
- Orchestration layer

---

## Success Criteria

Foundation Phase complete when:

- ✅ **Single command ingestion**: `orbit ingest --source attack`
- ✅ **Deterministic outputs**: Hash of outputs identical across runs
- ✅ **Loud failures**: Invalid data produces clear error messages
- ✅ **Extensible**: New source added in <50 lines without touching core
- ✅ **Offline tests**: `pytest` runs without network, passes deterministically

---

## Out of Scope (Future Phases)

The following are **explicitly excluded** from Foundation Phase:

- **Graph Construction**: Building Neo4j nodes/edges (separate phase)
- **Query Interfaces**: API or query layer (separate phase)
- **Reasoning/Inference**: Cross-source linking, semantic reconciliation
- **Visualization**: Graph rendering, dashboards
- **Performance Optimization**: Beyond correctness requirements
- **Automated Enrichment**: External data augmentation

**Rule**: If it interprets data instead of ingesting it, it belongs in a future phase.

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-general adapter interface | Complexity, poor fit | Start simple, iterate with real sources |
| "Temporary" shortcuts in validation | Technical debt, unreliable output | Strict code review, no validation bypass |
| Mixing ingestion with transformation | Unclear boundaries, bugs | Enforce separation via testing |
| Accepting partial data | Inconsistent state | Atomic ingestion, all-or-nothing |

---

## References

- Phase Charter: `docs/PHASE_CHARTER.md` (if created)
- Contributing Guide: `docs/CONTRIBUTING.md`
- ATT&CK Analysis: `ATT&CK STIX Analysis Workflow (Conceptual).ipynb`
