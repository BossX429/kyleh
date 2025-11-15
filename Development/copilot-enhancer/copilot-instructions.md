# GitHub Copilot Instructions - System Monitor Project

## Project Context

This is a Python-based system security monitoring tool with the following architecture:

### Core Components
- **system_monitor/** - Core monitoring module
- **SecurityBot/** - Security automation and bot functionality
- **Tests** - pytest-based test suite

### Technology Stack
- Python 3.8+
- psutil for system metrics
- WMI for Windows-specific features
- pytest for testing
- black & isort for code formatting

## Code Style Guidelines

### Python Style
- Follow PEP 8 with black formatting (100 char line length)
- Use type hints for all function signatures
- Prefer descriptive variable names over abbreviations
- Use docstrings for all public functions and classes

### Example Function Format
```python
def monitor_cpu_usage(self, threshold: float = 80.0) -> Dict[str, Any]:
    """
    Monitor CPU usage and detect high usage patterns.
    
    Args:
        threshold: CPU usage percentage threshold for warnings
        
    Returns:
        Dictionary containing CPU metrics and warnings
    """
    # Implementation
```

### Testing Patterns
- One test file per module: `test_<module_name>.py`
- Use fixtures for common setup
- Mock external dependencies (WMI, psutil where needed)
- Aim for >80% code coverage

### File Organization
```
system_monitor/
├── __init__.py
├── monitor.py      # Main monitoring logic
└── version.py      # Version info
tests/
├── test_monitor.py
└── fixtures/       # Test data
```

## Common Tasks

### Adding New Monitoring Feature
1. Add method to SecurityMonitorBackend class
2. Add corresponding tests
3. Update API documentation if exposed
4. Add type hints and docstrings

### Creating Plugin
1. Follow template in PLUGIN_DEVELOPMENT.md
2. Implement required methods: __init__, start, stop, get_metrics
3. Add to plugins/ directory
4. Add plugin tests

### Security Considerations
- Never hardcode credentials
- Validate all user inputs
- Use proper exception handling for system calls
- Log security-relevant events
- Follow principle of least privilege

## Project-Specific Patterns

### Metrics Collection
```python
# Always use try/except for system calls
try:
    cpu_percent = psutil.cpu_percent(interval=0.1)
except psutil.Error as e:
    self.logger.error(f"Failed to get CPU metrics: {e}")
    return {}
```

### Configuration Management
- Use pyproject.toml for project metadata
- Environment-specific settings via .env (never committed)
- User preferences in config files

### Error Handling
```python
# Pattern: Log and return gracefully
try:
    result = risky_operation()
except SpecificException as e:
    self.logger.error(f"Operation failed: {e}")
    return default_safe_value
```

## Documentation Standards

- Keep README.md up to date with new features
- Update API.md when adding endpoints
- Document breaking changes in commit messages
- Use clear commit messages: `type(scope): description`

## Dependencies

When suggesting new dependencies:
1. Check if functionality exists in stdlib first
2. Prefer well-maintained packages with security track record
3. Consider cross-platform compatibility
4. Add to pyproject.toml with version constraints

## Testing Commands

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=system_monitor --cov-report=html

# Lint code
black .
isort .
mypy system_monitor/
```

## Known Limitations

- GPU monitoring requires GPUtil (optional dependency)
- Some features are Windows-only (WMI-based)
- Network latency requires elevated permissions on some systems

## Future Enhancements

- WebSocket support for real-time metrics streaming
- Plugin hot-reloading
- Multi-platform support (Linux, macOS)
- Advanced ML-based anomaly detection
