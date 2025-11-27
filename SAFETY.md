# Safety Checklist - Before Deploying

## ✓ Fixed Issues

### Critical Fixes Applied
- [x] **Auto-optimization DISABLED** - Won't automatically throttle processes
- [x] **Process whitelist added** - Ollama, Python, VSCode, Claude protected
- [x] **Memory clearing fixed** - Uses proper Windows API instead of fake cmdlet
- [x] **Security scanner disabled** - Reduces false positives
- [x] **Relative paths** - Works from any directory
- [x] **Thresholds tuned** - Optimized for 64GB RAM / 7900XTX

### ML Model Status
- **Current state**: Untrained RandomForest model exists but unused
- **Actual optimization**: Uses rule-based logic (CPU/RAM thresholds)
- **Impact**: None - ML code path not active
- **Future**: Train model with real data or remove entirely

### Security Scanner Status
- **Current state**: Disabled by default
- **Why**: Too many false positives, outdated signatures
- **If enabled**: High CPU threshold (90%), no network monitoring
- **Recommendation**: Keep disabled until improved

## Pre-Flight Checks

### Before Running Monitor
1. **Test GPU detection**
   ```powershell
   python -c "from gpu_monitor import GPUMonitor; print(GPUMonitor().get_metrics())"
   ```

2. **Verify config loads**
   ```powershell
   python test.py
   ```

3. **Check logs directory exists**
   ```powershell
   dir logs\
   ```

### Before Enabling Auto-Optimization
1. **Run in monitoring mode for 24 hours**
   - Watch what it would recommend
   - Check logs for false positives
   - Verify whitelist covers your apps

2. **Test priority changes manually**
   ```powershell
   # Check current priorities
   Get-Process | Select-Object Name, PriorityClass | Sort-Object Name
   ```

3. **Add critical processes to whitelist**
   - Games you play
   - Rendering software
   - Any 24/7 services

### Before Installing as Service
1. **Verify it runs stable in console**
   ```powershell
   python monitor.py
   # Let run for 1+ hour, check for crashes
   ```

2. **Test with high load**
   - Run Ollama inference
   - Open multiple browser tabs
   - Start VSCode with extensions
   - Check alerts are reasonable

3. **Review log output**
   ```powershell
   Get-Content logs\monitor.log -Tail 50
   ```

## Safe Deployment Steps

### Phase 1: Monitoring Only (Current State)
- Auto-optimization: OFF
- Security scanning: OFF
- Just watch and log
- Run: `python monitor.py`

### Phase 2: Optimization Testing (After 24hrs)
- Review recommendations in logs
- If reasonable, enable: `"auto_optimize": true`
- Monitor for 48 hours
- Check if any whitelisted process got throttled (shouldn't happen)

### Phase 3: Service Deployment (After stable)
- Install as Windows service
- Configure to start automatically
- Monitor system behavior
- Keep logs size under control

## Emergency Recovery

### If Something Goes Wrong

**Monitor is throttling important process:**
1. Stop monitor: Ctrl+C
2. Add process to whitelist in config.json
3. Restart monitor

**System feels slow:**
1. Check logs: `Get-Content logs\monitor.log -Tail 50`
2. Disable auto-optimization: Set `"auto_optimize": false`
3. Restart monitor

**Service won't stop:**
```powershell
Get-Service | Where-Object {$_.Name -like "*kyleh*"} | Stop-Service -Force
```

**Complete reset:**
```powershell
# Stop everything
python service_wrapper.py remove

# Reset config to defaults
git checkout config.json

# Start fresh
python monitor.py
```

## What's Safe to Enable Now

✅ **Safe to use immediately:**
- Monitoring (CPU/RAM/GPU/Disk)
- Threshold alerts
- Logging to file
- Console output

⚠️ **Test first (current state):**
- Optimization recommendations (logged only)
- Process whitelist (verify coverage)

❌ **Keep disabled:**
- Auto-optimization (until tested)
- Security scanning (too noisy)
- Network monitoring (false positives)

## Monitoring Best Practices

### Daily Use
- Glance at console output periodically
- Check logs weekly: `logs\monitor.log`
- Note any unexpected alerts
- Update whitelist as you install new software

### For AI Development Sessions
- Start monitor before heavy Ollama work
- Watch GPU temp during long inference
- Check VRAM usage with large models
- Look for memory leaks after hours of use

### Red Flags to Watch For
- Repeated critical alerts (investigate cause)
- Unknown processes with high CPU (check logs)
- GPU temp consistently >85°C (cooling issue?)
- RAM never dropping below 90% (memory leak?)

## Future Improvements

When you're ready:
1. Train the ML model with real system data
2. Improve security scanner with behavioral analysis
3. Add dashboard/web UI for remote monitoring
4. Integrate with Windows Performance Monitor
5. Add alerting (email/Discord/Slack)
