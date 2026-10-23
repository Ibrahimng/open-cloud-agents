---
name: pytest-test-suite
description: Author comprehensive unit, integration, and async test suites in Python using pytest, fixtures, monkeypatching, and pytest-asyncio.
---

# Pytest Production Test Suite Guidelines

## Standards & Best Practices
1. **Directory Structure**: Mirror `src/` inside `tests/` (e.g. `src/services/billing.py` ➔ `tests/services/test_billing.py`).
2. **Fixtures over Shared State**: Use explicit `@pytest.fixture` with appropriate scopes (`function`, `session`).
3. **Async Testing**: Use `pytest-asyncio` with `@pytest.mark.asyncio`.

## Reference Test Suite with Mocking & Parametrization

```python
import pytest
from unittest.mock import AsyncMock
from src.services.tax_calculator import calculate_tax

@pytest.fixture
def mock_currency_service():
    service = AsyncMock()
    service.get_exchange_rate.return_value = 1.25
    return service

@pytest.mark.parametrize("subtotal,rate,expected_tax", [
    (100.0, 0.20, 20.0),
    (50.0, 0.10, 5.0),
    (0.0, 0.20, 0.0),
])
def test_calculate_tax_parametrized(subtotal, rate, expected_tax):
    tax = calculate_tax(subtotal=subtotal, tax_rate=rate)
    assert tax == pytest.approx(expected_tax, 0.01)

@pytest.mark.asyncio
async def test_currency_conversion_async(mock_currency_service):
    rate = await mock_currency_service.get_exchange_rate("GBP", "USD")
    assert rate == 1.25
    mock_currency_service.get_exchange_rate.assert_awaited_once_with("GBP", "USD")
```

## Running Tests with Coverage
```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=85
```
