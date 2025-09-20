"""
Security Bot Enterprise - Threat Detection Engine
Advanced multi-vector threat detection with real-time monitoring
"""

import os
import time
import psutil
import sqlite3
import hashlib
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False


class ThreatDetectionEngine:
    """Advanced threat detection with multiple monitoring vectors"""
    
    def __init__(self, db_path="security_bot.db"):
        self.db_path = db_path
        self.monitoring = False
        self.setup_logging()
        self.setup_database()
        
        # Initialize monitors
        self.network_monitor = NetworkMonitor(self)
        self.file_monitor = FileIntegrityMonitor(self)
        self.process_monitor = ProcessAnalyzer(self)
        if WINREG_AVAILABLE:
            self.registry_monitor = RegistryMonitor(self)
        
        self.logger.info("Threat Detection Engine initialized")
    
    def setup_logging(self):
        """Setup threat detection logging"""
        self.logger = logging.getLogger('ThreatDetection')
    
    def setup_database(self):
        """Setup threat detection database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    threat_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source_ip TEXT,
                    target_ip TEXT,
                    process_name TEXT,
                    file_path TEXT,
                    registry_key TEXT,
                    description TEXT,
                    details TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error("Database setup failed: %s", e)
    
    def start_monitoring(self):
        """Start all monitoring components"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.logger.info("Starting threat detection monitoring...")
        
        # Start network monitoring
        network_thread = threading.Thread(target=self.network_monitor.start, daemon=True)
        network_thread.start()
        
        # Start file monitoring
        file_thread = threading.Thread(target=self.file_monitor.start, daemon=True)
        file_thread.start()
        
        # Start process monitoring
        process_thread = threading.Thread(target=self.process_monitor.start, daemon=True)
        process_thread.start()
        
        # Start registry monitoring (Windows only)
        if WINREG_AVAILABLE and hasattr(self, 'registry_monitor'):
            registry_thread = threading.Thread(target=self.registry_monitor.start, daemon=True)
            registry_thread.start()
        
        self.logger.info("All monitoring components started")
    
    def stop_monitoring(self):
        """Stop all monitoring components"""
        self.monitoring = False
        self.logger.info("Stopping threat detection monitoring...")
    
    def log_threat(self, threat_type: str, severity: str, **kwargs):
        """Log detected threat to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO threats (threat_type, severity, source_ip, target_ip, 
                                   process_name, file_path, registry_key, description, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                threat_type,
                severity,
                kwargs.get('source_ip'),
                kwargs.get('target_ip'),
                kwargs.get('process_name'),
                kwargs.get('file_path'),
                kwargs.get('registry_key'),
                kwargs.get('description', ''),
                json.dumps(kwargs.get('details', {}))
            ))
            
            threat_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.warning("Threat detected: %s (%s) - ID: %d", threat_type, severity, threat_id)
            return threat_id
            
        except Exception as e:
            self.logger.error("Failed to log threat: %s", e)
            return None


class NetworkMonitor:
    """Network traffic analysis and threat detection"""
    
    def __init__(self, engine: ThreatDetectionEngine):
        self.engine = engine
        self.logger = logging.getLogger('NetworkMonitor')
        self.suspicious_ips = set()
        self.connection_counts = {}
        
    def start(self):
        """Start network monitoring"""
        self.logger.info("Network monitoring started")
        
        while self.engine.monitoring:
            try:
                self.analyze_network_connections()
                self.check_suspicious_activity()
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error("Network monitoring error: %s", e)
                time.sleep(10)
    
    def analyze_network_connections(self):
        """Analyze current network connections"""
        try:
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.raddr:  # Remote address exists
                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port
                    
                    # Track connection counts
                    if remote_ip not in self.connection_counts:
                        self.connection_counts[remote_ip] = 0
                    self.connection_counts[remote_ip] += 1
                    
                    # Check for suspicious ports
                    if self.is_suspicious_port(remote_port):
                        self.engine.log_threat(
                            'suspicious_port',
                            'medium',
                            source_ip=conn.laddr.ip if conn.laddr else 'unknown',
                            target_ip=remote_ip,
                            description=f'Connection to suspicious port {remote_port}',
                            details={'port': remote_port, 'status': conn.status}
                        )
                    
                    # Check for suspicious IPs
                    if self.is_suspicious_ip(remote_ip):
                        self.engine.log_threat(
                            'suspicious_ip',
                            'high',
                            source_ip=conn.laddr.ip if conn.laddr else 'unknown',
                            target_ip=remote_ip,
                            description=f'Connection to suspicious IP {remote_ip}',
                            details={'port': remote_port, 'status': conn.status}
                        )
                        
        except Exception as e:
            self.logger.error("Network analysis error: %s", e)
    
    def check_suspicious_activity(self):
        """Check for suspicious network activity patterns"""
        try:
            # Check for excessive connections from single IP
            for ip, count in self.connection_counts.items():
                if count > 100:  # Threshold for suspicious activity
                    self.engine.log_threat(
                        'excessive_connections',
                        'high',
                        source_ip=ip,
                        description=f'Excessive connections from {ip}: {count}',
                        details={'connection_count': count}
                    )
            
            # Reset counters periodically
            if len(self.connection_counts) > 1000:
                self.connection_counts.clear()
                
        except Exception as e:
            self.logger.error("Suspicious activity check error: %s", e)
    
    def is_suspicious_port(self, port: int) -> bool:
        """Check if port is commonly used by malware"""
        suspicious_ports = {
            1337, 31337, 12345, 54321, 9999, 6666, 6667, 1234, 
            4444, 5555, 7777, 8888, 1080, 3128, 8080, 1433, 3389
        }
        return port in suspicious_ports
    
    def is_suspicious_ip(self, ip: str) -> bool:
        """Check if IP is known to be suspicious"""
        # This could be enhanced with threat intelligence feeds
        suspicious_patterns = ['10.0.0.', '192.168.1.', '172.16.']
        return any(ip.startswith(pattern) for pattern in suspicious_patterns)


class FileIntegrityMonitor:
    """File system integrity monitoring"""
    
    def __init__(self, engine: ThreatDetectionEngine):
        self.engine = engine
        self.logger = logging.getLogger('FileIntegrityMonitor')
        self.monitored_dirs = [
            'C:\\Windows\\System32',
            'C:\\Program Files',
            'C:\\Users'
        ]
        self.file_hashes = {}
    
    def start(self):
        """Start file integrity monitoring"""
        self.logger.info("File integrity monitoring started")
        
        # Initial scan
        self.scan_directories()
        
        while self.engine.monitoring:
            try:
                self.check_file_changes()
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error("File monitoring error: %s", e)
                time.sleep(30)
    
    def scan_directories(self):
        """Scan monitored directories for baseline"""
        self.logger.info("Performing initial file scan...")
        
        for directory in self.monitored_dirs:
            if os.path.exists(directory):
                try:
                    self.scan_directory(directory)
                except Exception as e:
                    self.logger.error("Error scanning %s: %s", directory, e)
    
    def scan_directory(self, directory: str):
        """Scan a single directory"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files[:10]:  # Limit to first 10 files per directory
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.isfile(file_path):
                            file_hash = self.calculate_file_hash(file_path)
                            if file_hash:
                                self.file_hashes[file_path] = file_hash
                    except (PermissionError, OSError):
                        continue  # Skip files we can't access
                        
        except Exception as e:
            self.logger.error("Directory scan error for %s: %s", directory, e)
    
    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA-256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256()
                chunk = f.read(8192)
                while chunk:
                    file_hash.update(chunk)
                    chunk = f.read(8192)
                return file_hash.hexdigest()
                
        except Exception:
            return None
    
    def check_file_changes(self):
        """Check for file modifications"""
        try:
            for file_path, original_hash in list(self.file_hashes.items())[:50]:  # Check subset
                if os.path.exists(file_path):
                    current_hash = self.calculate_file_hash(file_path)
                    if current_hash and current_hash != original_hash:
                        self.engine.log_threat(
                            'file_modification',
                            'medium',
                            file_path=file_path,
                            description=f'File modified: {file_path}',
                            details={
                                'original_hash': original_hash,
                                'current_hash': current_hash
                            }
                        )
                        # Update hash
                        self.file_hashes[file_path] = current_hash
                        
        except Exception as e:
            self.logger.error("File change check error: %s", e)


class ProcessAnalyzer:
    """Process behavior analysis"""
    
    def __init__(self, engine: ThreatDetectionEngine):
        self.engine = engine
        self.logger = logging.getLogger('ProcessAnalyzer')
        self.process_baseline = {}
    
    def start(self):
        """Start process monitoring"""
        self.logger.info("Process monitoring started")
        
        while self.engine.monitoring:
            try:
                self.analyze_processes()
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error("Process monitoring error: %s", e)
                time.sleep(10)
    
    def analyze_processes(self):
        """Analyze running processes"""
        try:
            current_processes = {}
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    pid = proc_info['pid']
                    name = proc_info['name']
                    
                    current_processes[pid] = proc_info
                    
                    # Check for high resource usage
                    if proc_info['cpu_percent'] > 80:
                        self.engine.log_threat(
                            'high_cpu_usage',
                            'medium',
                            process_name=name,
                            description=f'High CPU usage by {name}: {proc_info["cpu_percent"]:.1f}%',
                            details=proc_info
                        )
                    
                    if proc_info['memory_percent'] > 50:
                        self.engine.log_threat(
                            'high_memory_usage',
                            'medium',
                            process_name=name,
                            description=f'High memory usage by {name}: {proc_info["memory_percent"]:.1f}%',
                            details=proc_info
                        )
                    
                    # Check for suspicious process names
                    if self.is_suspicious_process(name):
                        self.engine.log_threat(
                            'suspicious_process',
                            'high',
                            process_name=name,
                            description=f'Suspicious process detected: {name}',
                            details=proc_info
                        )
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.process_baseline = current_processes
            
        except Exception as e:
            self.logger.error("Process analysis error: %s", e)
    
    def is_suspicious_process(self, name: str) -> bool:
        """Check if process name is suspicious"""
        suspicious_names = [
            'keylogger', 'trojan', 'virus', 'malware', 'backdoor',
            'rootkit', 'stealer', 'miner', 'botnet', 'ransomware'
        ]
        return any(sus in name.lower() for sus in suspicious_names)


class RegistryMonitor:
    """Windows Registry monitoring (Windows only)"""
    
    def __init__(self, engine: ThreatDetectionEngine):
        self.engine = engine
        self.logger = logging.getLogger('RegistryMonitor')
        self.monitored_keys = [
            r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
            r'HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
        ]
    
    def start(self):
        """Start registry monitoring"""
        if not WINREG_AVAILABLE:
            self.logger.warning("Registry monitoring not available (not Windows)")
            return
        
        self.logger.info("Registry monitoring started")
        
        while self.engine.monitoring:
            try:
                self.check_registry_changes()
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error("Registry monitoring error: %s", e)
                time.sleep(60)
    
    def check_registry_changes(self):
        """Check for registry modifications"""
        try:
            for key_path in self.monitored_keys:
                self.monitor_registry_key(key_path)
                
        except Exception as e:
            self.logger.error("Registry check error: %s", e)
    
    def monitor_registry_key(self, key_path: str):
        """Monitor specific registry key"""
        try:
            # Parse key path
            if key_path.startswith('HKEY_LOCAL_MACHINE'):
                hkey = winreg.HKEY_LOCAL_MACHINE
                subkey = key_path.replace('HKEY_LOCAL_MACHINE\\', '')
            elif key_path.startswith('HKEY_CURRENT_USER'):
                hkey = winreg.HKEY_CURRENT_USER
                subkey = key_path.replace('HKEY_CURRENT_USER\\', '')
            else:
                return
            
            # Open and enumerate registry key
            try:
                with winreg.OpenKey(hkey, subkey) as key:
                    i = 0
                    while True:
                        try:
                            name, value, value_type = winreg.EnumValue(key, i)
                            
                            # Check for suspicious entries
                            if self.is_suspicious_registry_entry(name, value):
                                self.engine.log_threat(
                                    'suspicious_registry',
                                    'medium',
                                    registry_key=key_path,
                                    description=f'Suspicious registry entry: {name}',
                                    details={'name': name, 'value': str(value), 'type': value_type}
                                )
                            
                            i += 1
                            
                        except OSError:
                            break  # No more values
                            
            except FileNotFoundError:
                pass  # Key doesn't exist
                
        except Exception as e:
            self.logger.error("Registry key monitoring error for %s: %s", key_path, e)
    
    def is_suspicious_registry_entry(self, name: str, value: str) -> bool:
        """Check if registry entry is suspicious"""
        suspicious_patterns = [
            'temp', 'download', 'script', 'powershell', 'cmd',
            'malware', 'trojan', 'backdoor', 'keylogger'
        ]
        
        value_str = str(value).lower()
        name_str = name.lower()
        
        return any(pattern in value_str or pattern in name_str for pattern in suspicious_patterns)


if __name__ == '__main__':
    # Test threat detection
    engine = ThreatDetectionEngine()
    engine.start_monitoring()
    
    try:
        # Run for 30 seconds for testing
        time.sleep(30)
    except KeyboardInterrupt:
        pass
    finally:
        engine.stop_monitoring()
        print("Threat detection stopped")