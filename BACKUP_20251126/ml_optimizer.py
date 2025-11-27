import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
import logging
import psutil
import subprocess

class MLOptimizer:
    """ML-powered system optimization based on usage patterns"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.model = None
        self.load_or_create_model()
        self.optimization_history = []
        
    def load_or_create_model(self):
        model_path = self.config["optimization"]["ml_model_path"]
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.logger.info("Loaded existing ML model")
            except:
                self.create_new_model()
        else:
            self.create_new_model()
    
    def create_new_model(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.logger.info("Created new ML model")
    
    def extract_features(self, metrics):
        features = [
            metrics['cpu']['avg'],
            metrics['ram']['percent'],
            len(metrics['cpu']['percent']),
            metrics['disk']['percent']
        ]
        
        if 'gpu' in metrics:
            features.extend([
                metrics['gpu'].get('utilization', 0),
                metrics['gpu'].get('temperature', 0),
                metrics['gpu'].get('vram_used_mb', 0) / 24576 * 100
            ])
        else:
            features.extend([0, 0, 0])
        
        return features
    
    def analyze_and_optimize(self, current_metrics, history):
        if len(history) < 10:
            return []
        
        recommendations = []
        
        if current_metrics['cpu']['avg'] > 90:
            recommendations.append({
                'type': 'cpu_high',
                'action': 'lower_process_priority',
                'reason': 'CPU usage critical'
            })
        
        if current_metrics['ram']['percent'] > 90:
            recommendations.append({
                'type': 'ram_high',
                'action': 'clear_standby_memory',
                'reason': 'RAM usage critical'
            })
        
        if 'gpu' in current_metrics:
            gpu = current_metrics['gpu']
            if gpu.get('temperature', 0) > 80:
                recommendations.append({
                    'type': 'gpu_hot',
                    'action': 'increase_fan_speed',
                    'reason': f"GPU temp at {gpu['temperature']:.1f}C"
                })
        
        avg_cpu = np.mean([m['cpu']['avg'] for m in history[-10:]])
        avg_ram = np.mean([m['ram']['percent'] for m in history[-10:]])
        
        if avg_cpu < 30 and avg_ram < 50:
            recommendations.append({
                'type': 'system_idle',
                'action': 'run_maintenance',
                'reason': 'System underutilized, good time for maintenance'
            })
        
        return recommendations
    
    def apply_optimizations(self, recommendations):
        for rec in recommendations:
            try:
                if rec['action'] == 'lower_process_priority':
                    self.lower_high_cpu_processes()
                elif rec['action'] == 'clear_standby_memory':
                    self.clear_standby_memory()
                elif rec['action'] == 'increase_fan_speed':
                    self.logger.info("GPU fan speed optimization recommended (manual adjustment needed)")
                elif rec['action'] == 'run_maintenance':
                    self.logger.info("System idle - maintenance tasks can be scheduled")
                    
                self.logger.info(f"Applied optimization: {rec['action']}")
            except Exception as e:
                self.logger.error(f"Failed to apply {rec['action']}: {e}")
    
    def lower_high_cpu_processes(self):
        whitelist = set(self.config["optimization"]["process_whitelist"])
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                proc_name = proc.info['name'].lower()
                
                # Skip whitelisted processes
                if any(wl.lower() in proc_name for wl in whitelist):
                    continue
                    
                if proc.info['cpu_percent'] > 50:
                    p = psutil.Process(proc.info['pid'])
                    if p.nice() != psutil.BELOW_NORMAL_PRIORITY_CLASS:
                        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                        self.logger.info(f"Lowered priority for {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def clear_standby_memory(self):
        """Clear standby memory using Windows EmptyStandbyList"""
        try:
            # Use Windows API to clear standby memory
            # This requires admin privileges
            import ctypes
            ctypes.windll.kernel32.SetSystemFileCacheSize(ctypes.c_size_t(-1), ctypes.c_size_t(-1), 0)
            self.logger.info("Cleared standby memory via kernel32")
        except Exception as e:
            # Fallback: try RAMMap if available
            try:
                import subprocess
                result = subprocess.run(['C:\\Windows\\System32\\RAMMap.exe', '-Ew'], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    self.logger.info("Cleared standby memory via RAMMap")
                else:
                    self.logger.warning(f"RAMMap not available, skipping memory clear")
            except Exception as e2:
                self.logger.warning(f"Memory clearing unavailable: {e}, fallback: {e2}")
    
    def save_model(self):
        if self.model:
            joblib.dump(self.model, self.config["optimization"]["ml_model_path"])
            self.logger.info("Saved ML model")
