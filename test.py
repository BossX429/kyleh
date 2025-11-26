"""
Test script to verify KyleH System Monitor components
"""
import sys
import os

print("KyleH System Monitor - Component Test")
print("=" * 50)

# Test 1: Check dependencies
print("\n[1] Testing Python dependencies...")
deps = [
    ('psutil', 'psutil'),
    ('numpy', 'numpy'),
    ('pandas', 'pandas'),
    ('sklearn', 'sklearn.ensemble'),
    ('joblib', 'joblib')
]
missing = []
for name, import_path in deps:
    try:
        __import__(import_path)
        print(f"  OK: {name}")
    except ImportError:
        print(f"  MISSING: {name}")
        missing.append(name)

if missing:
    print(f"\nMissing dependencies: {', '.join(missing)}")
    print("Run: python setup.py")
    sys.exit(1)

# Test 2: Check configuration
print("\n[2] Testing configuration...")
try:
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    print("  OK: config.json loaded")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)

# Test 3: Check modules
print("\n[3] Testing monitor modules...")
try:
    from monitor import SystemMonitor
    print("  OK: monitor.py")
except Exception as e:
    print(f"  ERROR: monitor.py - {e}")
    
try:
    from gpu_monitor import GPUMonitor
    print("  OK: gpu_monitor.py")
except Exception as e:
    print(f"  ERROR: gpu_monitor.py - {e}")
    
try:
    from ml_optimizer import MLOptimizer
    print("  OK: ml_optimizer.py")
except Exception as e:
    print(f"  ERROR: ml_optimizer.py - {e}")
    
try:
    from security_scanner import SecurityScanner
    print("  OK: security_scanner.py")
except Exception as e:
    print(f"  ERROR: security_scanner.py - {e}")

# Test 4: Quick system check
print("\n[4] Testing system metrics...")
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    print(f"  CPU: {cpu:.1f}%")
    print(f"  RAM: {ram:.1f}%")
    print("  OK: System metrics accessible")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 5: GPU detection
print("\n[5] Testing GPU detection...")
try:
    gpu_mon = GPUMonitor()
    gpu_metrics = gpu_mon.get_metrics()
    print(f"  GPU: {gpu_metrics['name']}")
    print(f"  Temp: {gpu_metrics['temperature']:.1f}C")
    print(f"  VRAM: {gpu_metrics['vram_used_mb']:.0f}MB / {gpu_metrics['vram_total_mb']:.0f}MB")
    print("  OK: GPU monitoring functional")
except Exception as e:
    print(f"  WARNING: GPU monitoring may not be fully functional - {e}")

print("\n" + "=" * 50)
print("Component test complete!")
print("\nNext steps:")
print("  1. Run monitor: python monitor.py")
print("  2. Install service: python install_service.py (as Admin)")
