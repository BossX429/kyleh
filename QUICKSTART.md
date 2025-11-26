# Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   python setup.py
   ```

2. **Test the monitor:**
   ```bash
   python monitor.py
   ```
   Press Ctrl+C to stop.

3. **Install as Windows Service (requires Admin):**
   ```bash
   python install_service.py
   ```

## Usage

### Running Manually
```bash
python monitor.py
```

### Service Management
```bash
# Start service
python service_wrapper.py start

# Stop service
python service_wrapper.py stop

# Restart service
python service_wrapper.py restart

# Remove service
python service_wrapper.py remove
```

## Configuration

Edit `config.json` to customize:

- **Monitoring intervals**: How often to check system metrics
- **Alert thresholds**: CPU/RAM/GPU warning and critical levels
- **Optimization settings**: Auto-optimization and ML parameters
- **Security scanning**: Process whitelist and scan frequency

## Monitoring Output

The monitor displays real-time information:
```
[2024-11-25 23:30:45]
CPU: 45.2% | RAM: 62.1% (39.8GB/64.0GB)
GPU: 32.5% | Temp: 65.0C | VRAM: 8192MB/24576MB
```

## Alerts

System generates alerts for:
- High CPU usage (>80% warning, >95% critical)
- High RAM usage (>85% warning, >95% critical)
- High GPU temperature (>75C warning, >85C critical)
- Security threats (suspicious processes, unsigned executables)

## Logs

Check logs at: `C:\Projects\kyleh\logs\monitor.log`

## Troubleshooting

**GPU monitoring not working?**
- Install AMD drivers
- Install ROCm tools (optional)
- Check GPU is detected: `rocm-smi`

**Service won't start?**
- Run as Administrator
- Check logs for errors
- Verify all dependencies installed
