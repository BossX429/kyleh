import psutil
import time
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from gpu_monitor import GPUMonitor
from ml_optimizer import MLOptimizer
from security_scanner import SecurityScanner

class SystemMonitor:
    def __init__(self, config_path="config.json"):
        self.load_config(config_path)
        self.setup_logging()
        self.gpu_monitor = GPUMonitor() if self.config["monitoring"]["enable_gpu"] else None
        self.ml_optimizer = MLOptimizer(self.config) if self.config["monitoring"]["enable_optimization"] else None
        self.security_scanner = SecurityScanner(self.config) if self.config["monitoring"]["enable_security"] else None
        self.metrics_history = []
        
    def load_config(self, config_path):
        # Get absolute path relative to script location
        script_dir = Path(__file__).parent
        config_path = script_dir / config_path if not Path(config_path).is_absolute() else Path(config_path)
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Handle relative paths in config
        log_file = Path(self.config["monitoring"]["log_file"])
        if not log_file.is_absolute():
            log_file = script_dir / log_file
        self.config["monitoring"]["log_file"] = str(log_file)
        
        os.makedirs(log_file.parent, exist_ok=True)
        
    def setup_logging(self):
        logging.basicConfig(
            filename=self.config["monitoring"]["log_file"],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def get_system_metrics(self):
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1, percpu=True),
                'avg': psutil.cpu_percent(interval=1),
                'freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'temp': self.get_cpu_temp()
            },
            'ram': {
                'percent': psutil.virtual_memory().percent,
                'used_gb': psutil.virtual_memory().used / (1024**3),
                'total_gb': psutil.virtual_memory().total / (1024**3),
                'available_gb': psutil.virtual_memory().available / (1024**3)
            },
            'disk': {
                'percent': psutil.disk_usage('C:\\').percent,
                'used_gb': psutil.disk_usage('C:\\').used / (1024**3),
                'free_gb': psutil.disk_usage('C:\\').free / (1024**3)
            }
        }
        
        if self.gpu_monitor:
            metrics['gpu'] = self.gpu_monitor.get_metrics()
            
        return metrics
    
    def get_cpu_temp(self):
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            temperature_infos = w.Sensor()
            for sensor in temperature_infos:
                if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                    return sensor.Value
        except:
            return None
        return None
    
    def check_thresholds(self, metrics):
        alerts = []
        thresholds = self.config["thresholds"]
        
        if metrics['cpu']['avg'] > thresholds['cpu_critical']:
            alerts.append(f"CRITICAL: CPU usage at {metrics['cpu']['avg']:.1f}%")
        elif metrics['cpu']['avg'] > thresholds['cpu_warning']:
            alerts.append(f"WARNING: CPU usage at {metrics['cpu']['avg']:.1f}%")
            
        if metrics['ram']['percent'] > thresholds['ram_critical']:
            alerts.append(f"CRITICAL: RAM usage at {metrics['ram']['percent']:.1f}%")
        elif metrics['ram']['percent'] > thresholds['ram_warning']:
            alerts.append(f"WARNING: RAM usage at {metrics['ram']['percent']:.1f}%")
        
        if self.gpu_monitor and 'gpu' in metrics:
            gpu = metrics['gpu']
            if gpu.get('temperature', 0) > thresholds['gpu_temp_critical']:
                alerts.append(f"CRITICAL: GPU temp at {gpu['temperature']:.1f}C")
            elif gpu.get('temperature', 0) > thresholds['gpu_temp_warning']:
                alerts.append(f"WARNING: GPU temp at {gpu['temperature']:.1f}C")
                
            if gpu.get('vram_used_mb', 0) > thresholds['gpu_vram_critical']:
                alerts.append(f"CRITICAL: GPU VRAM at {gpu['vram_used_mb']:.0f}MB")
            elif gpu.get('vram_used_mb', 0) > thresholds['gpu_vram_warning']:
                alerts.append(f"WARNING: GPU VRAM at {gpu['vram_used_mb']:.0f}MB")
        
        return alerts
    
    def run_optimization(self, metrics):
        if self.ml_optimizer:
            recommendations = self.ml_optimizer.analyze_and_optimize(metrics, self.metrics_history)
            if recommendations:
                self.logger.info(f"Optimization recommendations: {recommendations}")
                if self.config["optimization"]["auto_optimize"]:
                    self.ml_optimizer.apply_optimizations(recommendations)
    
    def run_security_scan(self):
        if self.security_scanner:
            threats = self.security_scanner.scan()
            if threats:
                for threat in threats:
                    self.logger.warning(f"Security threat detected: {threat}")
                return threats
        return []
    
    def monitor_loop(self):
        self.logger.info("System monitor started")
        print("KyleH System Monitor started. Press Ctrl+C to stop.")
        
        last_optimization = time.time()
        last_security_scan = time.time()
        
        try:
            while True:
                metrics = self.get_system_metrics()
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-1000:]
                
                alerts = self.check_thresholds(metrics)
                for alert in alerts:
                    self.logger.warning(alert)
                    print(f"[ALERT] {alert}")
                
                current_time = time.time()
                if current_time - last_optimization > self.config["optimization"]["optimization_interval"]:
                    self.run_optimization(metrics)
                    last_optimization = current_time
                
                if current_time - last_security_scan > self.config["security"]["scan_interval"]:
                    self.run_security_scan()
                    last_security_scan = current_time
                
                self.print_status(metrics)
                time.sleep(self.config["monitoring"]["interval_seconds"])
                
        except KeyboardInterrupt:
            self.logger.info("Monitor stopped by user")
            print("\nMonitor stopped.")
    
    def print_status(self, metrics):
        print(f"\n[{metrics['timestamp']}]")
        print(f"CPU: {metrics['cpu']['avg']:.1f}% | RAM: {metrics['ram']['percent']:.1f}% ({metrics['ram']['used_gb']:.1f}GB/{metrics['ram']['total_gb']:.1f}GB)")
        if 'gpu' in metrics:
            gpu = metrics['gpu']
            print(f"GPU: {gpu.get('utilization', 0):.1f}% | Temp: {gpu.get('temperature', 0):.1f}C | VRAM: {gpu.get('vram_used_mb', 0):.0f}MB/{gpu.get('vram_total_mb', 0):.0f}MB")

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.monitor_loop()
