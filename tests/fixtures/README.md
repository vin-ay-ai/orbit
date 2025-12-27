# Test Fixtures

This directory contains deterministic test data for offline test execution.

## Guidelines

- **Minimal fixtures**: Keep test data small and focused
- **Version controlled**: All fixtures committed to git
- **No external dependencies**: Tests must run offline
- **Deterministic**: Fixtures produce consistent test results
- **Well-documented**: Each fixture should have clear purpose

## Fixture Types

### STIX Bundles

Minimal STIX bundles for testing ATT&CK adapter:
- Valid bundles with different object types
- Invalid bundles for error testing
- Edge cases (empty bundles, malformed objects)

### D3FEND Data

Placeholder for D3FEND test data (future).

## Adding New Fixtures

When adding a new fixture:

1. Keep it minimal (only necessary fields)
2. Add clear comments explaining purpose
3. Use in deterministic tests
4. Verify it produces consistent results

Example:

```json
{
  "type": "bundle",
  "id": "bundle--test-001",
  "objects": [
    {
      "type": "attack-pattern",
      "id": "attack-pattern--12345678-1234-1234-1234-123456789abc",
      "created": "2023-01-01T00:00:00.000Z",
      "modified": "2023-01-01T00:00:00.000Z",
      "name": "Test Attack Pattern"
    }
  ]
}
```
