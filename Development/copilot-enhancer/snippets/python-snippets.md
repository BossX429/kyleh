# Python Code Snippets for System Monitor

## Monitor Class Template

```python
from typing import Dict, Any, Optional
import logging

class CustomMonitor:
    """
    Template for custom monitoring class.
    
    Attributes:
        name: Monitor name
        enabled: Whether monitoring is enabled
        logger: Logger instance
    """
    
    def __init__(self, name: str = "CustomMonitor") -> None:
        """Initialize the monitor."""
        self.name = name
        self.enabled = True
        self.logger = logging.getLogger(__name__)
        self._setup()
    
    def _setup(self) -> None:
        """Perform initial setup."""
        self.logger.info(f"{self.name} initialized")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Collect and return metrics.
        
        Returns:
            Dictionary containing collected metrics
        """
        if not self.enabled:
            return {}
        
        try:
            metrics = self._collect_metrics()
            return {
                "timestamp": self._get_timestamp(),
                "metrics": metrics,
                "status": "ok"
            }
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return {"status": "error", "message": str(e)}
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Implement metric collection logic."""
        # TODO: Implement metric collection
        return {}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def start(self) -> None:
        """Start monitoring."""
        self.enabled = True
        self.logger.info(f"{self.name} started")
    
    def stop(self) -> None:
        """Stop monitoring."""
        self.enabled = False
        self.logger.info(f"{self.name} stopped")
```

## Error Handler Decorator

```python
from functools import wraps
import logging
from typing import Callable, Any

def handle_errors(default_return: Any = None, log_error: bool = True):
    """
    Decorator to handle errors gracefully.
    
    Args:
        default_return: Value to return on error
        log_error: Whether to log the error
    
    Usage:
        @handle_errors(default_return={}, log_error=True)
        def risky_function():
            # Function that might raise exceptions
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger = logging.getLogger(func.__module__)
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                return default_return
        return wrapper
    return decorator
```

## Retry Logic

```python
import time
from functools import wraps
from typing import Callable, Type, Tuple

def retry(max_attempts: int = 3, delay: float = 1.0, 
          exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        exceptions: Tuple of exceptions to catch
    
    Usage:
        @retry(max_attempts=3, delay=1.0, exceptions=(ConnectionError,))
        def unstable_operation():
            # Operation that might fail
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = delay * (2 ** attempt)
                        time.sleep(sleep_time)
            raise last_exception
        return wrapper
    return decorator
```

## Metric History Tracker

```python
from collections import deque
from typing import Any, List, Optional
from datetime import datetime

class MetricHistory:
    """
    Track metric history with size limit.
    
    Usage:
        history = MetricHistory(max_size=100)
        history.add(42.5)
        avg = history.average()
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize metric history.
        
        Args:
            max_size: Maximum number of data points to store
        """
        self.max_size = max_size
        self.data = deque(maxlen=max_size)
        self.timestamps = deque(maxlen=max_size)
    
    def add(self, value: float) -> None:
        """Add a data point."""
        self.data.append(value)
        self.timestamps.append(datetime.now())
    
    def average(self) -> Optional[float]:
        """Calculate average of all data points."""
        if not self.data:
            return None
        return sum(self.data) / len(self.data)
    
    def latest(self) -> Optional[float]:
        """Get the most recent value."""
        return self.data[-1] if self.data else None
    
    def min(self) -> Optional[float]:
        """Get minimum value."""
        return min(self.data) if self.data else None
    
    def max(self) -> Optional[float]:
        """Get maximum value."""
        return max(self.data) if self.data else None
    
    def get_range(self, count: int) -> List[float]:
        """
        Get the last N data points.
        
        Args:
            count: Number of data points to retrieve
            
        Returns:
            List of most recent data points
        """
        return list(self.data)[-count:]
    
    def clear(self) -> None:
        """Clear all history."""
        self.data.clear()
        self.timestamps.clear()
```

## Configuration Manager

```python
import json
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    """
    Simple configuration management.
    
    Usage:
        config = ConfigManager("config.json")
        value = config.get("key", default="default_value")
        config.set("key", "new_value")
        config.save()
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
    
    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.
        
        Args:
            updates: Dictionary of updates
        """
        self.config.update(updates)
```

## Plugin Base Class

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class PluginBase(ABC):
    """
    Base class for all plugins.
    
    All plugins must inherit from this class and implement required methods.
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        Initialize plugin.
        
        Args:
            name: Plugin name
            version: Plugin version
        """
        self.name = name
        self.version = version
        self.enabled = True
    
    @abstractmethod
    def start(self) -> None:
        """Called when plugin is loaded."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Called when plugin is unloaded."""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """
        Return plugin metrics.
        
        Returns:
            Dictionary containing plugin data
        """
        pass
    
    def check(self) -> Dict[str, Any]:
        """
        Perform plugin health check.
        
        Returns:
            Dictionary with check results
        """
        return {
            "checks_passed": True,
            "warnings": [],
            "errors": []
        }
```
