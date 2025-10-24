# Plugin Development Guide

> Learn how to create custom plugins for the Security Monitor system

## 🎯 Overview

The Security Monitor supports custom plugins to extend functionality. Plugins can monitor games, applications, or system metrics and report telemetry back to the main system.

## 📋 Plugin Structure

### Basic Plugin Template

```python
"""
Example Plugin for Security Monitor
"""

class MyPlugin:
    """
    Custom plugin template
    """
    
    def __init__(self):
        self.name = "My Plugin"
        self.version = "1.0.0"
        self.enabled = True
        
    def start(self):
        """Called when plugin is loaded"""
        print(f"{self.name} v{self.version} started")
        
    def stop(self):
        """Called when plugin is unloaded"""
        print(f"{self.name} stopped")
        
    def get_metrics(self):
        """
        Return plugin metrics
        
        Returns:
            dict: Plugin telemetry data
        """
        return {
            "plugin_name": self.name,
            "version": self.version,
            "status": "active" if self.enabled else "inactive",
            "custom_metric": 42
        }
        
    def check(self):
        """
        Perform plugin checks (called each monitoring iteration)
        
        Returns:
            dict: Check results
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "checks_passed": True,
            "warnings": [],
            "errors": []
        }
```

## 🔧 Plugin Capabilities

### 1. Game/Application Monitoring

Monitor specific games or applications:

```python
import psutil
from pathlib import Path

class GameMonitorPlugin:
    """
    Monitor game performance and status
    """
    
    def __init__(self, game_name, exe_name):
        self.name = f"{game_name} Monitor"
        self.game_name = game_name
        self.exe_name = exe_name
        self.process = None
        
    def is_running(self):
        """Check if game is running"""
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['name'] == self.exe_name:
                    self.process = proc
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
        
    def get_metrics(self):
        """Get game performance metrics"""
        if not self.is_running():
            return {
                "game": self.game_name,
                "running": False
            }
            
        try:
            return {
                "game": self.game_name,
                "running": True,
                "cpu_percent": self.process.cpu_percent(interval=0.1),
                "memory_mb": self.process.memory_info().rss / 1024 / 1024,
                "threads": self.process.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"game": self.game_name, "running": False}
```

### 2. Custom Metric Collection

Collect custom system metrics:

```python
import GPUtil

class GPUMonitorPlugin:
    """
    Advanced GPU monitoring
    """
    
    def __init__(self):
        self.name = "GPU Monitor"
        
    def get_metrics(self):
        """Get detailed GPU metrics"""
        gpus = GPUtil.getGPUs()
        
        if not gpus:
            return {"error": "No GPUs detected"}
            
        gpu = gpus[0]  # Primary GPU
        
        return {
            "gpu_name": gpu.name,
            "gpu_load": gpu.load * 100,
            "gpu_memory_used_mb": gpu.memoryUsed,
            "gpu_memory_total_mb": gpu.memoryTotal,
            "gpu_memory_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100,
            "gpu_temperature": gpu.temperature
        }
```

### 3. Security Checks

Implement custom security validations:

```python
import socket
import subprocess

class NetworkSecurityPlugin:
    """
    Monitor network security indicators
    """
    
    def __init__(self):
        self.name = "Network Security"
        self.suspicious_ports = [22, 23, 3389, 5900]  # SSH, Telnet, RDP, VNC
        
    def check_open_ports(self):
        """Check for suspicious open ports"""
        warnings = []
        
        for port in self.suspicious_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                warnings.append(f"Port {port} is open (potential security risk)")
                
        return warnings
        
    def check(self):
        """Run security checks"""
        return {
            "timestamp": datetime.now().isoformat(),
            "warnings": self.check_open_ports(),
            "checks_passed": len(self.check_open_ports()) == 0
        }
```

## 📦 Plugin Installation

### Directory Structure

```
kyleh/
├── plugins/
│   ├── __init__.py
│   ├── game_monitor.py
│   ├── gpu_advanced.py
│   └── network_security.py
```

### Loading Plugins

The Security Monitor automatically loads plugins from the `plugins/` directory:

```python
# In security_monitor_backend.py
def _load_plugins(self):
    """Load plugins from plugins directory"""
    plugin_dir = Path(__file__).parent / "plugins"
    
    if not plugin_dir.exists():
        return
        
    for plugin_file in plugin_dir.glob("*.py"):
        if plugin_file.name.startswith("_"):
            continue
            
        # Dynamic plugin loading
        spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find plugin classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, 'get_metrics'):
                plugin = obj()
                self.plugins[plugin.name] = plugin
                plugin.start()
```

## 🔌 Plugin API Reference

### Required Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `__init__()` | Initialize plugin | None |
| `start()` | Called when plugin loads | None |
| `stop()` | Called when plugin unloads | None |
| `get_metrics()` | Return plugin data | dict |

### Optional Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `check()` | Perform checks | dict with `checks_passed`, `warnings`, `errors` |
| `optimize()` | Optimization routine | None |
| `on_alert(alert)` | Handle system alerts | None |

### Plugin Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | str | Yes | Plugin display name |
| `version` | str | No | Plugin version |
| `enabled` | bool | No | Enable/disable flag |
| `description` | str | No | Plugin description |

## 🚀 Advanced Examples

### Full-Featured Game Plugin

```python
import psutil
import time
from datetime import datetime
from pathlib import Path

class AdvancedGamePlugin:
    """
    Comprehensive game monitoring with FPS tracking
    """
    
    def __init__(self, game_name, exe_name, config_path=None):
        self.name = f"{game_name} Monitor Pro"
        self.version = "2.0.0"
        self.game_name = game_name
        self.exe_name = exe_name
        self.config_path = config_path
        self.enabled = True
        
        # Performance history
        self.cpu_history = []
        self.mem_history = []
        self.fps_history = []
        
        # Thresholds
        self.cpu_threshold = 80.0
        self.mem_threshold_mb = 4096
        
    def start(self):
        """Initialize plugin"""
        print(f"[{self.name}] Starting v{self.version}")
        if self.config_path:
            self._load_config()
            
    def stop(self):
        """Cleanup"""
        print(f"[{self.name}] Stopping")
        self._save_metrics()
        
    def _load_config(self):
        """Load plugin configuration"""
        if Path(self.config_path).exists():
            with open(self.config_path) as f:
                config = json.load(f)
                self.cpu_threshold = config.get('cpu_threshold', 80.0)
                self.mem_threshold_mb = config.get('mem_threshold_mb', 4096)
                
    def _save_metrics(self):
        """Save metrics to file"""
        metrics_file = Path(f"{self.game_name}_metrics.json")
        with open(metrics_file, 'w') as f:
            json.dump({
                "cpu_avg": sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0,
                "mem_avg": sum(self.mem_history) / len(self.mem_history) if self.mem_history else 0,
                "sessions": len(self.cpu_history)
            }, f, indent=2)
            
    def get_metrics(self):
        """Comprehensive metrics"""
        for proc in psutil.process_iter(['name', 'exe', 'cpu_percent', 'memory_info', 'num_threads']):
            try:
                if proc.info['name'] == self.exe_name:
                    cpu = proc.cpu_percent(interval=0.1)
                    mem_mb = proc.info['memory_info'].rss / 1024 / 1024
                    
                    # Track history
                    self.cpu_history.append(cpu)
                    self.mem_history.append(mem_mb)
                    
                    # Limit history size
                    if len(self.cpu_history) > 100:
                        self.cpu_history = self.cpu_history[-100:]
                        self.mem_history = self.mem_history[-100:]
                    
                    return {
                        "game": self.game_name,
                        "running": True,
                        "cpu_percent": cpu,
                        "cpu_avg": sum(self.cpu_history) / len(self.cpu_history),
                        "memory_mb": mem_mb,
                        "memory_avg": sum(self.mem_history) / len(self.mem_history),
                        "threads": proc.info['num_threads'],
                        "warnings": self._check_thresholds(cpu, mem_mb)
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return {"game": self.game_name, "running": False}
        
    def _check_thresholds(self, cpu, mem_mb):
        """Check performance thresholds"""
        warnings = []
        
        if cpu > self.cpu_threshold:
            warnings.append(f"High CPU usage: {cpu:.1f}%")
            
        if mem_mb > self.mem_threshold_mb:
            warnings.append(f"High memory usage: {mem_mb:.0f}MB")
            
        return warnings
        
    def check(self):
        """Health check"""
        metrics = self.get_metrics()
        return {
            "timestamp": datetime.now().isoformat(),
            "checks_passed": len(metrics.get('warnings', [])) == 0,
            "warnings": metrics.get('warnings', []),
            "errors": []
        }
        
    def optimize(self):
        """Game-specific optimizations"""
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['name'] == self.exe_name:
                    # Boost priority
                    proc.nice(psutil.HIGH_PRIORITY_CLASS)
                    print(f"[{self.name}] Boosted game priority")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
```

## 📝 Best Practices

1. **Error Handling** - Always wrap external calls in try/except
2. **Performance** - Keep `get_metrics()` fast (< 100ms)
3. **Resources** - Clean up in `stop()` method
4. **Logging** - Use descriptive messages for debugging
5. **Configuration** - Support external config files
6. **History** - Limit data history to prevent memory leaks
7. **Documentation** - Include docstrings for all public methods

## 🧪 Testing Plugins

```python
# test_plugin.py
import unittest

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyPlugin()
        
    def test_plugin_initialization(self):
        self.assertEqual(self.plugin.name, "My Plugin")
        self.assertTrue(self.plugin.enabled)
        
    def test_get_metrics(self):
        metrics = self.plugin.get_metrics()
        self.assertIn("plugin_name", metrics)
        self.assertEqual(metrics["plugin_name"], "My Plugin")
        
    def test_check(self):
        result = self.plugin.check()
        self.assertIn("checks_passed", result)
        self.assertIsInstance(result["checks_passed"], bool)
```

## 📚 Further Reading

- [Main README](README.md) - Project overview
- [API Documentation](API.md) - REST API reference
- [Backend Architecture](backend_frontend_mapping.md) - System design

---

**Plugin SDK Version:** 0.1.0  
**Last Updated:** October 2025
