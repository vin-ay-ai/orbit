# Contributing to Orbit

## Foundation Phase Development Guide

This guide covers development practices for the Foundation Phase: building a deterministic ingestion architecture.

---

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- Neo4j 5.0+ (for future phases, not required for ingestion development)

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd orbit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available

# Run tests to verify setup
pytest
```

---

## Project Structure

```
orbit/
├── src/orbit/              # Core package
│   ├── ingestion/          # Ingestion orchestration
│   ├── adapters/           # Source adapters
│   ├── schemas/            # Data models & validation
│   └── loaders.py          # Legacy (will be refactored)
├── tests/                  # Test suite
│   ├── fixtures/           # Test data
│   └── test_*.py           # Test modules
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     # System architecture
│   └── CONTRIBUTING.md     # This file
├── playground/             # Experimentation workspace
└── data/                   # Source data files
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow the architectural principles (see below).

### 3. Write Tests

**Required**: All new code must have tests.

```bash
# Run specific test file
pytest tests/test_adapters.py

# Run all tests
pytest

# Run with coverage
pytest --cov=src/orbit
```

### 4. Verify Determinism

Critical requirement: Same inputs → same outputs

```bash
# Run test twice, verify outputs are identical
pytest tests/test_ingestion.py -v
pytest tests/test_ingestion.py -v

# Check that fixture-based tests produce consistent results
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new adapter for X"

# Commit message format:
# feat: new feature
# fix: bug fix
# docs: documentation
# test: test additions/changes
# refactor: code refactoring
```

### 6. Run Full Test Suite

```bash
pytest
```

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

---

## Adding a New Source Adapter

### Step-by-Step Guide

#### 1. Create Adapter File

Create `src/orbit/adapters/newsource.py`:

```python
from pathlib import Path
from typing import Any

from .base import SourceAdapter, RawData


class NewSourceAdapter(SourceAdapter):
    """Adapter for NewSource threat intelligence data."""

    def __init__(self, data_path: Path):
        self.data_path = data_path

    def fetch(self) -> RawData:
        """Load raw data from source."""
        with open(self.data_path, 'r') as f:
            return json.load(f)

    def normalize(self, raw: RawData) -> list[dict[str, Any]]:
        """Convert to internal representation."""
        # Transform source format to standard structure
        normalized = []
        for item in raw['items']:
            normalized.append({
                'id': item['id'],
                'type': item['type'],
                # ... additional fields
            })
        return normalized

    @property
    def source_name(self) -> str:
        return "newsource"
```

#### 2. Register Adapter

Update `src/orbit/adapters/__init__.py`:

```python
from .attack import AttackAdapter
from .d3fend import D3FENDAdapter
from .newsource import NewSourceAdapter

ADAPTERS = {
    "attack": AttackAdapter,
    "d3fend": D3FENDAdapter,
    "newsource": NewSourceAdapter,
}

def get_adapter(source: str) -> SourceAdapter:
    if source not in ADAPTERS:
        raise ValueError(f"Unknown source: {source}")
    return ADAPTERS[source]
```

#### 3. Create Test Fixture

Add `tests/fixtures/newsource_sample.json`:

```json
{
  "items": [
    {
      "id": "test-001",
      "type": "example-type",
      "name": "Test Item"
    }
  ]
}
```

#### 4. Write Tests

Create `tests/test_adapters.py::test_newsource_adapter`:

```python
def test_newsource_adapter():
    """Test NewSource adapter fetch and normalize."""
    # Arrange
    fixture_path = Path("tests/fixtures/newsource_sample.json")
    adapter = NewSourceAdapter(fixture_path)

    # Act
    raw = adapter.fetch()
    normalized = adapter.normalize(raw)

    # Assert
    assert len(normalized) == 1
    assert normalized[0]['id'] == 'test-001'
    assert normalized[0]['type'] == 'example-type'


def test_newsource_adapter_determinism():
    """Test that adapter produces consistent outputs."""
    fixture_path = Path("tests/fixtures/newsource_sample.json")
    adapter = NewSourceAdapter(fixture_path)

    # Run twice
    result1 = adapter.normalize(adapter.fetch())
    result2 = adapter.normalize(adapter.fetch())

    # Should be identical
    assert result1 == result2
```

#### 5. Add Schema (if needed)

If new object types are introduced, add schemas in `src/orbit/schemas/`:

```python
class NewSourceObject(BaseModel):
    id: str
    type: str
    name: str

    @validator('type')
    def validate_type(cls, v):
        allowed = ['example-type', 'other-type']
        if v not in allowed:
            raise ValueError(f"Invalid type: {v}")
        return v
```

#### 6. Test End-to-End

```bash
pytest tests/test_adapters.py::test_newsource_adapter -v
```

---

## Architectural Principles (Enforceable)

### 1. Schemas are contracts

**DO**:
```python
class STIXObject(BaseModel):
    id: str = Field(..., regex=r'^[a-z-]+--[0-9a-f-]+$')
    type: str
```

**DON'T**:
```python
# Accepting any structure without validation
def load_object(data: dict):
    return data  # No validation!
```

### 2. Relationships are validated

**DO**:
```python
def validate_relationship(rel: dict) -> bool:
    if rel['type'] != 'relationship':
        raise ValueError("Not a relationship")
    if not is_valid_relationship_type(rel['relationship_type']):
        raise ValueError(f"Invalid relationship: {rel['relationship_type']}")
    return True
```

**DON'T**:
```python
# Assuming relationships are valid
def process_relationship(rel: dict):
    # No validation - dangerous!
    create_edge(rel['source_ref'], rel['target_ref'])
```

### 3. Reproducibility > convenience

**DO**:
```python
def ingest(source: str, data_path: Path) -> IngestResult:
    # Deterministic: same inputs → same outputs
    adapter = get_adapter(source)
    data = adapter.fetch(data_path)
    return sorted(adapter.normalize(data), key=lambda x: x['id'])
```

**DON'T**:
```python
def ingest(source: str) -> IngestResult:
    # Non-deterministic: time-dependent, random order
    timestamp = datetime.now()  # Changes each run!
    data = fetch_random_sample()  # Different data each time!
    return data
```

### 4. Adapters isolate volatility

**DO**:
```python
# Source-specific logic in adapter
class AttackAdapter:
    def normalize(self, raw):
        # Handle ATT&CK-specific structure
        return [self._parse_attack_object(obj) for obj in raw['objects']]
```

**DON'T**:
```python
# Source-specific logic in core pipeline
def ingest(source: str, data: dict):
    if source == 'attack':
        # ATT&CK-specific logic here - BAD!
        objects = data['objects']
    elif source == 'd3fend':
        # D3FEND-specific logic here - BAD!
        objects = data['items']
```

### 5. No silent coercion

**DO**:
```python
def validate_field(value: Any, expected_type: type):
    if not isinstance(value, expected_type):
        raise TypeError(f"Expected {expected_type}, got {type(value)}")
    return value
```

**DON'T**:
```python
def validate_field(value: Any, expected_type: type):
    # Silently converting - loses information!
    return expected_type(value)
```

---

## Testing Guidelines

### Required Tests

Every new component must have:

1. **Unit tests**: Test in isolation
2. **Determinism tests**: Same input → same output
3. **Error tests**: Invalid inputs produce clear errors

### Test Structure

```python
def test_component_happy_path():
    """Test normal operation."""
    # Arrange: Set up inputs
    input_data = create_test_fixture()

    # Act: Execute function
    result = process(input_data)

    # Assert: Verify output
    assert result.is_valid()
    assert len(result.objects) == expected_count


def test_component_determinism():
    """Test reproducible outputs."""
    input_data = create_test_fixture()

    result1 = process(input_data)
    result2 = process(input_data)

    assert result1 == result2  # Must be identical


def test_component_error_handling():
    """Test error cases."""
    invalid_data = create_invalid_fixture()

    with pytest.raises(ValidationError) as exc:
        process(invalid_data)

    assert "clear error message" in str(exc.value)
```

### Fixtures

- Store in `tests/fixtures/`
- Use minimal, focused samples
- Version control all fixtures
- No external dependencies (offline execution)

---

## Code Review Checklist

Before submitting PR, verify:

- [ ] All tests pass: `pytest`
- [ ] Tests are deterministic (run twice, same results)
- [ ] New code has test coverage
- [ ] No source-specific logic in core modules
- [ ] Schema validation is explicit
- [ ] Error messages are clear and actionable
- [ ] Documentation updated (if public API changed)
- [ ] No "temporary" shortcuts or TODOs
- [ ] Follows architectural principles

---

## Common Pitfalls

### ❌ Mixing ingestion with transformation

**Problem**:
```python
def ingest_attack(data):
    objects = load_stix(data)
    # BAD: Inferring relationships during ingestion
    inferred_edges = infer_tacti_relationships(objects)
    return objects + inferred_edges
```

**Solution**: Keep ingestion pure - inference belongs in a later phase.

### ❌ Accepting partial data

**Problem**:
```python
def ingest(data):
    valid_objects = []
    for obj in data:
        try:
            valid_objects.append(validate(obj))
        except ValidationError:
            # BAD: Silently skipping invalid objects
            continue
    return valid_objects
```

**Solution**: Fail loudly on invalid data, log errors clearly.

### ❌ Time-dependent behavior

**Problem**:
```python
def create_object(data):
    return {
        'id': data['id'],
        'ingested_at': datetime.now(),  # BAD: Non-deterministic!
    }
```

**Solution**: Avoid timestamps, random IDs, or other time-dependent values.

---

## Getting Help

- **Architecture questions**: See `docs/ARCHITECTURE.md`
- **ATT&CK structure**: See `ATT&CK STIX Analysis Workflow (Conceptual).ipynb`
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions

---

## Foundation Phase Completion Criteria

Your PR helps complete Foundation Phase if it contributes to:

- ✅ Single command ingestion
- ✅ Deterministic outputs (byte-identical across runs)
- ✅ Loud failures for invalid data
- ✅ Extensible adapter system
- ✅ Offline, deterministic tests

Keep these criteria in mind when contributing!
