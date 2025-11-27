# KyleH System Monitor - Tuning Guide

## Optimized for Your System

**Hardware Profile:**
- CPU: Intel i7-12700K (12 cores, 20 threads)
- RAM: 64GB DDR4
- GPU: AMD Radeon RX 7900 XTX (24GB VRAM)
- OS: Windows 11 Pro

## Current Configuration

### Monitoring Intervals
- **System check**: Every 5 seconds
- **Optimization check**: Every 5 minutes (300s)
- **Security scan**: Every 10 minutes (600s) - DISABLED by default

### Threshold Settings

#### CPU Thresholds (tuned for 12700K)
- **Warning**: 85% (17+ cores maxed)
- **Critical**: 98% (all cores saturated)
- Higher than default because your CPU can handle sustained load

#### RAM Thresholds (tuned for 64GB)
- **Warning**: 90% (57.6GB used)
- **Critical**: 97% (62GB used)
- Conservative thresholds - you have plenty of headroom

#### GPU Thresholds (tuned for 7900XTX)
- **Temperature Warning**: 80°C
- **Temperature Critical**: 90°C
- **VRAM Warning**: 20GB (20,000MB)
- **VRAM Critical**: 23GB (23,000MB)
- 7900XTX can handle 80°C+ during gaming/rendering

## Process Protection

### Whitelisted Processes (won't be throttled)
- **ollama.exe** - Local AI inference
- **ollama_llama_server.exe** - Ollama model server
- **python.exe / pythonw.exe** - Your development work
- **Code.exe** - VSCode and extensions
- **claude.exe** - Claude desktop app
- **msedge.exe / chrome.exe** - Browsers
- **rocm-smi.exe** - GPU monitoring

**Why whitelist?** These are your critical workflows. The optimizer will never lower their priority even under load.

## Safety Features

### Auto-Optimization: DISABLED
- Set to `false` by default for safety
- Won't automatically adjust process priorities
- Won't clear memory without your approval
- Recommendations logged only - you decide

### Security Scanner: DISABLED
- Disabled by default to reduce false positives
- High CPU detection raised to 90% threshold
- Network monitoring disabled (too noisy)
- Can be enabled in config.json if needed

## Recommended Workflow

### For Daily Use
1. Run monitor in console mode: `python monitor.py`
2. Watch for alerts and patterns
3. Review logs: `logs\monitor.log`

### For Background Monitoring
1. Keep auto-optimization OFF initially
2. Monitor alerts for a few days
3. If recommendations make sense, enable auto-optimization
4. Add more processes to whitelist as needed

### For AI Development Workloads
Your typical workload:
- **Ollama models**: High CPU/RAM usage is normal
- **VSCode**: Can spike during extensions/Copilot
- **Claude desktop**: Moderate but steady
- **Browser with Claude.ai**: RAM intensive

**Recommended settings:**
- Keep thresholds high to avoid false alarms
- Monitor GPU VRAM when running large models
- Watch for memory leaks during long sessions

## Performance Expectations

### Normal Operation
- **CPU**: 20-40% baseline, 60-80% during AI inference
- **RAM**: 40-60% baseline, 70-85% during heavy dev work
- **GPU**: 0-10% idle, 50-90% during Ollama inference
- **GPU Temp**: 40-50°C idle, 70-85°C under load

### When to Investigate
- CPU >90% for >5 minutes (outside Ollama work)
- RAM >95% sustained (possible memory leak)
- GPU temp >90°C (check cooling/fan curve)
- Unexpected process spikes (check logs)

## Customization Tips

### Adjusting Thresholds
Edit `config.json`:
```json
"thresholds": {
  "cpu_warning": 85,      // Increase if too many warnings
  "cpu_critical": 98,     // Leave high for real emergencies
  "ram_warning": 90,       // Safe for 64GB system
  "ram_critical": 97       // Emergency threshold
}
```

### Adding Processes to Whitelist
If optimizer throttles something important:
```json
"process_whitelist": [
  "ollama.exe",
  "your_app.exe"           // Add your process here
]
```

### Changing Monitoring Frequency
```json
"monitoring": {
  "interval_seconds": 5,              // System metrics
  "optimization_interval": 300,       // 5 minutes
  "scan_interval": 600                // 10 minutes
}
```

## Known Behaviors

### GPU Monitoring
- **ROCm available**: Full metrics (temp, VRAM, power, clock)
- **ROCm unavailable**: Falls back to WMI/GPUtil (limited data)
- Check if ROCm works: `rocm-smi` in PowerShell

### Memory Clearing
- Uses Windows kernel32 API (requires admin)
- Fallback to RAMMap if available
- Only triggers at 97%+ RAM usage
- Logs warning if unavailable

### Process Priority Changes
- Only affects processes >50% CPU
- Whitelisted processes are protected
- Changes logged for review
- Requires admin privileges to modify system processes
