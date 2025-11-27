# KyleH System Monitor - CHANGES APPLIED

## Summary of Fixes and Tuning

Applied on: November 26, 2025

### Configuration Changes (config.json)

**Safety Improvements:**
-  Disabled auto-optimization (`"auto_optimize": false`)
-  Disabled security scanning (`"enable_security": false`)
-  Changed to relative paths (no hardcoded C:\\ paths)

**Threshold Tuning for 64GB / 7900XTX:**
- CPU Warning: 80% → **85%** (higher threshold for 12700K)
- CPU Critical: 95% → **98%** (real emergency only)
- RAM Warning: 85% → **90%** (you have 64GB headroom)
- RAM Critical: 95% → **97%** (conservative but safe)
- GPU Temp Warning: 75°C → **80°C** (7900XTX runs hotter)
- GPU Temp Critical: 85°C → **90°C** (max safe temp)

**Process Protection Added:**
```
ollama.exe, ollama_llama_server.exe, python.exe, pythonw.exe,
Code.exe, claude.exe, msedge.exe, chrome.exe, rocm-smi.exe
```
These processes will never be throttled by optimizer.

### Code Fixes

**ml_optimizer.py:**
1.  Added whitelist checking before lowering process priorities
2.  Fixed memory clearing - now uses Windows kernel32 API
3.  Added RAMMap fallback if API unavailable
4.  Better error handling and logging

**monitor.py:**
1.  Fixed path handling - now works with relative paths
2.  Automatically resolves paths relative to script location
3.  Creates log directory if missing

**security_scanner.py:**
1.  Removed outdated threats (WannaCry, Cryptolocker)
2.  Raised CPU threshold: 80% → 90% (less false positives)
3.  Added baseline tracking for high CPU processes
4.  Respects whitelist properly
5.  Better severity classification

### New Documentation

**TUNING.md** (NEW)
- Hardware-specific configuration explained
- Threshold rationale for your system
- Process whitelist management
- Performance expectations
- Customization tips

**SAFETY.md** (NEW)
- Pre-flight safety checklist
- Fixed issues summary
- Deployment phases (monitoring → testing → service)
- Emergency recovery procedures
- What's safe to enable now

**CHANGES.md** (THIS FILE)
- Complete changelog of fixes
- Before/after comparisons
- What was changed and why

### What's Still Disabled (By Design)

**ML Model:**
- Status: Untrained RandomForest exists but inactive
- Current: Uses rule-based optimization logic
- Why: Need real data to train properly
- Impact: None - works fine without it
- Future: Train with your actual system data or remove

**Security Scanner:**
- Status: Disabled by default
- Why: Too many false positives
- If enabled: Only flags truly suspicious behavior
- Recommendation: Keep disabled until improved

**Auto-Optimization:**
- Status: Disabled by default
- Why: Need to verify behavior first
- Process: Monitor for 24hrs → Review → Enable if good
- Safety: Whitelist protects critical apps

## Before vs After

### Before (Unsafe)
-  Auto-throttled processes without whitelist
-  Could interfere with Ollama/VSCode/Claude
-  Memory clearing used fake PowerShell cmdlet
-  Security scanner too noisy (WannaCry checks)
-  Conservative thresholds (false alarms)
-  Hardcoded paths (wouldn't work elsewhere)

### After (Safe)
-  Whitelist protects your critical apps
-  Auto-optimization disabled by default
-  Memory clearing uses proper Windows API
-  Security scanner disabled (optional enable)
-  Thresholds tuned for 64GB/7900XTX
-  Relative paths work from anywhere

## Testing the Changes

### Quick Test
```powershell
cd C:\Projects\kyleh
python test.py
```

Should output:
- All dependencies OK
- All modules load successfully
- System metrics accessible
- GPU detected (if ROCm available)

### Run the Monitor
```powershell
python monitor.py
```

Watch for:
- Real-time metrics display
- Appropriate alert thresholds
- No auto-optimization actions
- Clean log output

### Expected Console Output
```
KyleH System Monitor started. Press Ctrl+C to stop.

[2025-11-26 13:45:30]
CPU: 32.5% | RAM: 58.2% (37.3GB/64.0GB)
GPU: 15.0% | Temp: 65.0C | VRAM: 4096MB/24576MB

[2025-11-26 13:45:35]
CPU: 28.1% | RAM: 58.3% (37.3GB/64.0GB)
GPU: 12.0% | Temp: 64.0C | VRAM: 4096MB/24576MB
```

No alerts unless thresholds are actually exceeded.

## Next Steps

### Immediate (Safe to do now)
1. Run `python test.py` - Verify everything works
2. Run `python monitor.py` - Start monitoring
3. Let it run for a few hours
4. Check `logs\monitor.log` - Review output

### Short-term (After 24hrs monitoring)
1. Review optimization recommendations in logs
2. Check if whitelist covers all your apps
3. Consider enabling auto-optimization if recommendations are good
4. Add more processes to whitelist as needed

### Long-term (When stable)
1. Install as Windows service for 24/7 monitoring
2. Train ML model with your real system data
3. Improve security scanner or remove it
4. Add dashboard/web UI for remote monitoring

## Files Changed
- `config.json` - Thresholds, whitelist, safety settings
- `ml_optimizer.py` - Whitelist check, memory clearing fix
- `monitor.py` - Relative path handling
- `security_scanner.py` - Reduced false positives
- `README.md` - Updated docs
- `TUNING.md` - NEW hardware-specific guide
- `SAFETY.md` - NEW deployment checklist
- `CHANGES.md` - NEW this file
