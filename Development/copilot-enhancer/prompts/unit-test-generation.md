# Unit Test Generation Prompt

Use this prompt to generate comprehensive unit tests for Python modules.

## Prompt Template

```
Generate comprehensive unit tests for the following Python module:

[PASTE MODULE CODE HERE]

Requirements:
- Use pytest framework
- Include fixtures for common test data
- Mock external dependencies (psutil, wmi, network calls)
- Test both success and error cases
- Aim for >80% code coverage
- Follow existing test patterns in tests/ directory
- Use descriptive test function names: test_<functionality>_<scenario>
- Add docstrings to test functions explaining what is being tested

Test categories to include:
1. Happy path tests
2. Edge cases
3. Error handling
4. Input validation
5. State management (if applicable)

Example test structure:
```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_function_success_case(sample_data):
    \"\"\"Test function succeeds with valid input.\"\"\"
    # Arrange
    # Act
    # Assert
    
def test_function_invalid_input():
    \"\"\"Test function handles invalid input gracefully.\"\"\"
    # Arrange
    # Act
    # Assert
```
```

## Usage

1. Copy the module code you want to test
2. Replace `[PASTE MODULE CODE HERE]` with your code
3. Submit to GitHub Copilot
4. Review and customize generated tests
5. Add to tests/ directory with filename test_<module_name>.py

## Example

For a module `monitor.py`:
- Generated tests go in `tests/test_monitor.py`
- Use fixtures from `tests/conftest.py` if available
- Ensure tests can run with `pytest tests/test_monitor.py`
