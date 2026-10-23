# Pytest Fixtures & Parametrization Cheat Sheet

## 1. Fixture Scopes
- `function` (Default): Re-executed for each test method. Isolates mutations.
- `module`: Executed once per test file. Great for spinning up local SQLite DBs.
- `session`: Executed once per full test run. Ideal for container spinning (Testcontainers).

## 2. Yield Fixtures for Teardown
```python
import pytest

@pytest.fixture
def managed_temp_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("initial data")
    yield f
    # Cleanup execution occurs after test exits
    if f.exists():
        f.unlink()
```

## 3. Monkeypatching Environment Variables
```python
def test_production_flag_disabled(monkeypatch):
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("DEBUG", "true")
    assert is_debug_mode() is True
```
