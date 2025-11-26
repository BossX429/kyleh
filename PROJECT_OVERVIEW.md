# KyleH System Monitor - Project Overview

## Purpose
Real-time Windows system monitor optimized for high-performance gaming/development workstations. Specifically designed for systems with AMD 7900XTX GPUs and modern hardware.

## Core Features

### 1. System Monitoring
- **CPU**: Per-core and aggregate usage, frequency, temperature
- **RAM**: Usage percentage, available/used/total in GB
- **GPU**: AMD 7900XTX specific monitoring (utilization, temperature, VRAM)
- **Disk**: Usage statistics for C: drive

### 2. ML-Powered Optimization
- Analyzes usage patterns over time
- Automatically adjusts process priorities during high load
- Clears standby memory when RAM is critical
- Schedules maintenance during idle periods
- Learns from system behavior to optimize proactively

### 3. Security Scanning
- Detects suspicious processes (malware signatures)
- Monitors for unsigned executables
- Tracks unusual network connections
- Alerts on suspicious port usage
- Process whitelisting support

### 4. Automated Responses
- Lowers priority of high-CPU processes
- Clears standby memory when needed
- Logs all actions and alerts
- Configurable auto-optimization

## Architecture

### Core Components

**monitor.py** - Main orchestration engine
- Coordinates all monitoring activities
- Manages metric collection and history
- Triggers optimization and security scans
- Handles alerting and logging

**gpu_monitor.py** - AMD GPU monitoring
- ROCm-smi integration for direct GPU access
- Fallback to WMI and GPUtil for compatibility
- Tracks: utilization, temperature, VRAM, power, clock speed
- Optimized for AMD 7900XTX (24GB VRAM)

**ml_optimizer.py** - Machine learning optimization
- RandomForest classifier for pattern recognition
- Analyzes historical metrics for optimization opportunities
- Auto-adjusts process priorities
- Memory management (standby list clearing)
- Learns optimal configurations over time

**security_scanner.py** - Threat detection
- Process name scanning against known malware
- Unsigned executable detection
- Network connection monitoring
- Suspicious port detection
- Baseline behavior tracking

**service_wrapper.py** - Windows service integration
- Runs monitor as background Windows service
- Auto-start on boot
- Service lifecycle management

### Data Flow

1. **Metrics Collection** (every 5 seconds)
   - CPU/RAM/Disk via psutil
   - GPU via ROCm-smi or WMI
   - Network connections

2. **Threshold Checking**
   - Compare against configured limits
   - Generate alerts for warnings/criticals
   - Log all threshold breaches

3. **Optimization Analysis** (every 5 minutes)
   - ML model analyzes recent history
   - Generates optimization recommendations
   - Applies auto-optimizations if enabled

4. **Security Scanning** (every 10 minutes)
   - Process scanning
   - Network monitoring
   - Alert on suspicious activity

## Configuration

All settings in `config.json`:

- **Monitoring intervals**: Control scan frequency
- **Thresholds**: Warning/critical levels for all metrics
- **Optimization**: ML model path, learning rate, auto-optimization toggle
- **Security**: Whitelist, scan intervals, network monitoring
- **Alerts**: Notification preferences

## Hardware Optimization

### Intel 12700K
- Per-core monitoring (16 threads)
- Temperature tracking via WMI
- Frequency monitoring

### AMD 7900XTX (24GB VRAM)
- Direct ROCm integration
- Full VRAM tracking (24GB total)
- Temperature monitoring (warning: 75C, critical: 85C)
- Power consumption tracking
- Clock speed monitoring
- Utilization percentage

### 64GB RAM
- Real-time usage tracking
- Standby memory clearing when needed
- Available/used/total reporting
- Warning at 85%, critical at 95%

## Use Cases

1. **Gaming Performance**: Monitor GPU/CPU during gameplay, auto-optimize background processes
2. **Development Work**: Track resource usage during compilation, ensure system stability
3. **Security Monitoring**: Continuous threat detection for suspicious activity
4. **System Health**: Long-term trending and proactive optimization

## Future Enhancements

- Web dashboard for remote monitoring
- Discord/Slack notifications for critical alerts
- GPU overclocking recommendations
- Advanced ML models (LSTM for time-series prediction)
- Integration with Windows Performance Monitor
- Custom alert rules engine
- Multi-GPU support
- Cloud backup of metrics history

## Installation Steps

1. Clone repository
2. Run `python setup.py` to install dependencies
3. Configure `config.json` for your needs
4. Test: `python monitor.py`
5. Install service (Admin): `python install_service.py`
