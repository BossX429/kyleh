#!/usr/bin/env python3
"""Quick validation test for monitor fixes"""

print("Testing monitor initialization...")

from monitor import SystemMonitor

# Initialize monitor
m = SystemMonitor()
print(" Monitor initialized successfully")

# Get metrics
metrics = m.get_system_metrics()
print(f" CPU: {metrics['cpu']['avg']:.1f}%")
print(f" RAM: {metrics['ram']['percent']:.1f}% ({metrics['ram']['used_gb']:.1f}GB/{metrics['ram']['total_gb']:.1f}GB)")

if 'gpu' in metrics:
    print(f" GPU: {metrics['gpu']['utilization']:.1f}% @ {metrics['gpu']['temperature']:.1f}C")
else:
    print(" GPU monitoring attempted (may show zeros without WMI/GPUtil)")

# Check config
print(f"\nConfiguration:")
print(f"  Auto-optimize: {m.config['optimization']['auto_optimize']}")
print(f"  Security scan: {m.config['monitoring']['enable_security']}")
print(f"  Whitelisted processes: {len(m.config['optimization']['process_whitelist'])}")

print("\n All systems operational!")
print("\nReady to run: python monitor.py")
