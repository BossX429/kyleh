# KyleH System Monitor

Real-time Windows system monitor with ML-powered optimization and security scanning.

## Features

- Real-time CPU/RAM/GPU monitoring (AMD 7900XTX optimized)
- ML-powered performance optimization
- Security threat detection
- Auto-optimization based on usage patterns
- Windows service for background operation
- Detailed logging and alerting

## System Requirements

- Windows 10/11
- Python 3.10+
- AMD GPU (optimized for 7900XTX)
- Admin privileges for service installation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run monitor
python monitor.py

# Install as Windows service
python install_service.py
```

## Architecture

- `monitor.py` - Main monitoring engine
- `gpu_monitor.py` - AMD GPU monitoring
- `ml_optimizer.py` - ML-based optimization
- `security_scanner.py` - Threat detection
- `service_wrapper.py` - Windows service wrapper
- `config.json` - Configuration settings

## Configuration

Edit `config.json` to customize:
- Monitoring intervals
- Alert thresholds
- Optimization aggressiveness
- Security scan frequency
