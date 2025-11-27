import psutil
import logging
import hashlib
import os
from pathlib import Path

class SecurityScanner:
    """Security scanning for suspicious processes and activities"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        # Updated suspicious process list - modern threats
        self.suspicious_processes = [
            'mimikatz', 'psexec', 'pwdump', 'fgdump', 'wce',
            'nc.exe', 'netcat', 'ncat',
            # Add any others but keep it minimal
        ]
        self.process_baseline = {}
        self.network_baseline = {}
        self.known_high_cpu = set()  # Track legitimately high CPU processes
        
    def scan(self):
        threats = []
        threats.extend(self.scan_processes())
        
        if self.config["security"]["check_network"]:
            threats.extend(self.scan_network())
        
        return threats
    
    def scan_processes(self):
        threats = []
        whitelist = set(self.config["security"]["process_whitelist"])
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'connections']):
            try:
                name = proc.info['name'].lower()
                
                if any(susp in name for susp in self.suspicious_processes):
                    if name not in whitelist:
                        threats.append({
                            'type': 'suspicious_process',
                            'process': proc.info['name'],
                            'pid': proc.info['pid'],
                            'severity': 'high'
                        })
                
                if proc.info['exe']:
                    if self.check_unsigned_executable(proc.info['exe']):
                        threats.append({
                            'type': 'unsigned_executable',
                            'process': proc.info['name'],
                            'path': proc.info['exe'],
                            'pid': proc.info['pid'],
                            'severity': 'medium'
                        })
                
                # Check CPU usage - only flag truly unusual processes
                cpu_percent = proc.cpu_percent(interval=0.1)
                if cpu_percent > 90:  # Very high threshold
                    proc_key = f"{proc.info['name']}:{proc.info['pid']}"
                    if proc_key not in self.known_high_cpu and proc.info['name'].lower() not in whitelist:
                        # Only flag if sustained high CPU (not in baseline)
                        if proc.info['pid'] not in self.process_baseline:
                            threats.append({
                                'type': 'unusual_high_cpu',
                                'process': proc.info['name'],
                                'pid': proc.info['pid'],
                                'cpu_percent': cpu_percent,
                                'severity': 'low'
                            })
                            # Add to baseline after first detection
                            self.process_baseline[proc.info['pid']] = True
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return threats
    
    def scan_network(self):
        threats = []
        suspicious_ports = [4444, 5555, 6666, 31337, 12345]
        
        for conn in psutil.net_connections():
            try:
                if conn.laddr.port in suspicious_ports:
                    threats.append({
                        'type': 'suspicious_port',
                        'port': conn.laddr.port,
                        'address': conn.laddr.ip,
                        'status': conn.status,
                        'severity': 'high'
                    })
                
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    remote_key = f"{conn.raddr.ip}:{conn.raddr.port}"
                    if remote_key not in self.network_baseline:
                        self.network_baseline[remote_key] = True
                        
            except (AttributeError, psutil.AccessDenied):
                pass
        
        return threats
    
    def check_unsigned_executable(self, exe_path):
        try:
            if not os.path.exists(exe_path):
                return False
            
            import subprocess
            result = subprocess.run(
                ['powershell', '-Command', 
                 f'Get-AuthenticodeSignature "{exe_path}" | Select-Object -ExpandProperty Status'],
                capture_output=True, text=True, timeout=5
            )
            
            if 'NotSigned' in result.stdout:
                return True
        except:
            pass
        
        return False
