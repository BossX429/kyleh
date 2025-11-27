import subprocess
import re
import logging

class GPUMonitor:
    """Monitor AMD GPU using rocm-smi or fallback methods"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.use_rocm = self.check_rocm_available()
        self.gpu_name = "AMD 7900XTX"
        
    def check_rocm_available(self):
        try:
            result = subprocess.run(['rocm-smi', '--showtemp'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_metrics(self):
        if self.use_rocm:
            return self.get_metrics_rocm()
        else:
            return self.get_metrics_fallback()
    
    def get_metrics_rocm(self):
        metrics = {
            'name': self.gpu_name,
            'utilization': 0,
            'temperature': 0,
            'vram_used_mb': 0,
            'vram_total_mb': 24576,
            'power_watts': 0,
            'clock_mhz': 0
        }
        
        try:
            result = subprocess.run(['rocm-smi', '--showuse', '--showtemp', '--showmeminfo', 'vram', '--showpower'],
                                  capture_output=True, text=True, timeout=5)
            output = result.stdout
            
            temp_match = re.search(r'Temperature.*?(\d+\.?\d*)', output, re.IGNORECASE)
            if temp_match:
                metrics['temperature'] = float(temp_match.group(1))
            
            use_match = re.search(r'GPU use.*?(\d+)%', output, re.IGNORECASE)
            if use_match:
                metrics['utilization'] = int(use_match.group(1))
            
            vram_match = re.search(r'VRAM.*?(\d+).*?(\d+)', output, re.IGNORECASE)
            if vram_match:
                metrics['vram_used_mb'] = int(vram_match.group(1))
                metrics['vram_total_mb'] = int(vram_match.group(2))
            
            power_match = re.search(r'Average Graphics Package Power.*?(\d+\.?\d*)', output, re.IGNORECASE)
            if power_match:
                metrics['power_watts'] = float(power_match.group(1))
                
        except Exception as e:
            self.logger.error(f"Error reading ROCm metrics: {e}")
        
        return metrics
    
    def get_metrics_fallback(self):
        """Fallback method using Windows APIs and WMI"""
        metrics = {
            'name': self.gpu_name,
            'utilization': 0,
            'temperature': 0,
            'vram_used_mb': 0,
            'vram_total_mb': 24576,
            'power_watts': 0,
            'clock_mhz': 0
        }
        
        try:
            import wmi
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            
            for sensor in w.Sensor():
                if 'GPU' in sensor.Name or 'Radeon' in sensor.Name:
                    if sensor.SensorType == 'Temperature':
                        metrics['temperature'] = sensor.Value
                    elif sensor.SensorType == 'Load':
                        metrics['utilization'] = sensor.Value
                    elif sensor.SensorType == 'Power':
                        metrics['power_watts'] = sensor.Value
                    elif sensor.SensorType == 'Clock':
                        metrics['clock_mhz'] = sensor.Value
                        
        except Exception as e:
            self.logger.warning(f"WMI GPU monitoring not available: {e}")
            
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                metrics['utilization'] = gpu.load * 100
                metrics['temperature'] = gpu.temperature
                metrics['vram_used_mb'] = gpu.memoryUsed
                metrics['vram_total_mb'] = gpu.memoryTotal
        except Exception as e:
            self.logger.warning(f"GPUtil monitoring not available: {e}")
        
        return metrics
    
    def get_vram_percentage(self):
        metrics = self.get_metrics()
        if metrics['vram_total_mb'] > 0:
            return (metrics['vram_used_mb'] / metrics['vram_total_mb']) * 100
        return 0
