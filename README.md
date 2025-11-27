# KyleH System Monitor

Real-time Windows system monitor optimized for high-performance workstations.

**Designed for:**
- Intel i7-12700K (12 cores, 20 threads)
- 64GB DDR4 RAM
- AMD Radeon RX 7900 XTX (24GB VRAM)
- Windows 11 Pro

## Features

- **Real-time monitoring**: CPU/RAM/GPU/Disk metrics every 5 seconds
- **GPU optimization**: AMD 7900XTX specific monitoring with ROCm support
- **Smart alerts**: Tuned thresholds for high-end hardware
- **Process protection**: Whitelist for critical apps (Ollama, VSCode, Claude)
- **Safe by default**: Auto-optimization disabled until you're ready
- **Detailed logging**: Track system behavior and recommendations

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test components
python test.py

# Run monitor (safe monitoring mode)
python monitor.py
```

**Press Ctrl+C to stop**

## What It Does (Current Config)

✅ **Active:**
- Monitors CPU/RAM/GPU/Disk every 5 seconds
- Logs metrics to `logs\monitor.log`
- Displays real-time status in console
- Generates optimization recommendations (logged only)

❌ **Disabled for safety:**
- Auto-optimization (won't change process priorities)
- Security scanning (too many false positives)
- Memory clearing (until you enable it)

## Documentation

- **[TUNING.md](TUNING.md)** - Hardware-specific configuration explained
- **[SAFETY.md](SAFETY.md)** - Pre-flight checks and deployment phases
- **[QUICKSTART.md](QUICKSTART.md)** - Installation and usage guide
