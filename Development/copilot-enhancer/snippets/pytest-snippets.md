# Pytest Testing Snippets

## Basic Test Structure

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

def test_basic_functionality():
    """Test basic functionality with arrange-act-assert pattern."""
    # Arrange
    expected = 42
    
    # Act
    result = some_function()
    
    # Assert
    assert result == expected
```

## Fixtures

```python
@pytest.fixture
def sample_monitor():
    """Fixture providing a configured monitor instance."""
    from system_monitor import SecurityMonitor
    monitor = SecurityMonitor()
    yield monitor
    monitor.stop()  # Cleanup

@pytest.fixture
def mock_psutil():
    """Fixture providing mocked psutil."""
    with patch('psutil.cpu_percent') as mock_cpu:
        mock_cpu.return_value = 45.0
        yield mock_cpu

@pytest.fixture
def temp_config_file(tmp_path):
    """Fixture providing a temporary config file."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"key": "value"}')
    return config_file
```

## Parametrized Tests

```python
@pytest.mark.parametrize("input_value,expected", [
    (0, 0),
    (1, 1),
    (5, 25),
    (10, 100),
])
def test_square_function(input_value, expected):
    """Test square function with multiple inputs."""
    assert square(input_value) == expected

@pytest.mark.parametrize("threshold,should_alert", [
    (50, False),
    (80, False),
    (90, True),
    (100, True),
])
def test_cpu_alert_thresholds(threshold, should_alert):
    """Test CPU alerting at different thresholds."""
    result = check_cpu_alert(threshold)
    assert result == should_alert
```

## Mocking Examples

```python
def test_with_mock_object():
    """Test using Mock object."""
    mock_service = Mock()
    mock_service.get_data.return_value = {"key": "value"}
    
    result = process_data(mock_service)
    
    assert result is not None
    mock_service.get_data.assert_called_once()

@patch('system_monitor.monitor.psutil')
def test_with_patch_decorator(mock_psutil):
    """Test using patch decorator."""
    mock_psutil.cpu_percent.return_value = 75.0
    
    monitor = SecurityMonitor()
    result = monitor.get_cpu_usage()
    
    assert result == 75.0

def test_with_context_manager():
    """Test using patch as context manager."""
    with patch('system_monitor.monitor.psutil.cpu_percent') as mock_cpu:
        mock_cpu.return_value = 50.0
        result = get_cpu_metrics()
        assert result['cpu_percent'] == 50.0
```

## Exception Testing

```python
def test_raises_exception():
    """Test that function raises expected exception."""
    with pytest.raises(ValueError):
        invalid_operation()

def test_raises_exception_with_message():
    """Test exception with specific message."""
    with pytest.raises(ValueError, match="Invalid input"):
        invalid_operation("bad_input")

def test_no_exception_raised():
    """Test that function does not raise exception."""
    try:
        safe_operation()
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")
```

## Async Testing

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_operation()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_mock():
    """Test async function with mocking."""
    with patch('module.async_call') as mock_call:
        mock_call.return_value = asyncio.coroutine(lambda: "result")()
        result = await function_using_async_call()
        assert result == "result"
```

## Test Markers

```python
@pytest.mark.slow
def test_slow_operation():
    """Mark test as slow (can be skipped with -m "not slow")."""
    time.sleep(5)
    assert True

@pytest.mark.skipif(sys.platform == "win32", reason="Linux only")
def test_linux_specific():
    """Skip test on Windows."""
    assert True

@pytest.mark.xfail(reason="Known bug #123")
def test_known_failure():
    """Mark test as expected to fail."""
    assert False
```

## Coverage Helpers

```python
def test_all_code_paths():
    """Test multiple code paths for coverage."""
    # Test success path
    result = function_with_branches(valid=True)
    assert result.success
    
    # Test error path
    result = function_with_branches(valid=False)
    assert not result.success
    
    # Test edge case
    result = function_with_branches(edge_case=True)
    assert result.handled_edge_case
```

## Setup and Teardown

```python
class TestMonitorClass:
    """Test class with setup and teardown."""
    
    def setup_method(self):
        """Run before each test method."""
        self.monitor = SecurityMonitor()
    
    def teardown_method(self):
        """Run after each test method."""
        self.monitor.stop()
    
    def test_monitor_start(self):
        """Test monitor starts correctly."""
        self.monitor.start()
        assert self.monitor.is_running()
```

## Conftest Examples

```python
# tests/conftest.py
import pytest

@pytest.fixture(scope="session")
def session_config():
    """Session-wide configuration."""
    return {"test_mode": True}

@pytest.fixture(scope="module")
def module_resource():
    """Module-level resource (created once per test file)."""
    resource = expensive_setup()
    yield resource
    expensive_cleanup(resource)

@pytest.fixture(autouse=True)
def reset_state():
    """Automatically run before each test."""
    clear_global_state()
```
