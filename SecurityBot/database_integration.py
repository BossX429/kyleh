"""
Security Bot Enterprise - Database Integration
Advanced SQLite database with analytics and reporting capabilities
"""

import sqlite3
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import csv
import os


class DatabaseIntegration:
    """Enterprise database integration with analytics"""
    
    def __init__(self, db_path="security_bot.db"):
        self.db_path = db_path
        self.connection_pool = []
        self.pool_lock = threading.Lock()
        self.max_connections = 10
        self.setup_logging()
        self.init_database()
        self.create_indexes()
    
    def setup_logging(self):
        """Setup database logging"""
        self.logger = logging.getLogger('DatabaseIntegration')
    
    def get_connection(self):
        """Get database connection from pool"""
        with self.pool_lock:
            if self.connection_pool:
                return self.connection_pool.pop()
            else:
                conn = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30.0
                )
                conn.row_factory = sqlite3.Row
                return conn
    
    def return_connection(self, conn):
        """Return connection to pool"""
        with self.pool_lock:
            if len(self.connection_pool) < self.max_connections:
                self.connection_pool.append(conn)
            else:
                conn.close()
    
    def init_database(self):
        """Initialize all database tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Main threats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    threat_id TEXT UNIQUE NOT NULL,
                    threat_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source TEXT,
                    target TEXT,
                    description TEXT,
                    metadata TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    risk_score INTEGER DEFAULT 0
                )
            """)
            
            # Network monitoring table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS network_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_ip TEXT,
                    destination_ip TEXT,
                    source_port INTEGER,
                    destination_port INTEGER,
                    protocol TEXT,
                    bytes_sent INTEGER DEFAULT 0,
                    bytes_received INTEGER DEFAULT 0,
                    connection_duration REAL,
                    flags TEXT,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # File integrity monitoring
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_integrity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER,
                    last_modified TIMESTAMP,
                    monitored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    change_type TEXT,
                    previous_hash TEXT
                )
            """)
            
            # Process monitoring
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS process_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_id INTEGER NOT NULL,
                    process_name TEXT NOT NULL,
                    command_line TEXT,
                    parent_pid INTEGER,
                    cpu_percent REAL DEFAULT 0,
                    memory_percent REAL DEFAULT 0,
                    network_connections INTEGER DEFAULT 0,
                    file_operations INTEGER DEFAULT 0,
                    user_name TEXT,
                    start_time TIMESTAMP,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # System metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_in REAL,
                    network_out REAL,
                    active_connections INTEGER,
                    running_processes INTEGER,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Audit log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'success'
                )
            """)
            
            # Configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE NOT NULL,
                    config_value TEXT,
                    config_type TEXT DEFAULT 'string',
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT
                )
            """)
            
            conn.commit()
            self.return_connection(conn)
            
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize database: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
    
    def create_indexes(self):
        """Create database indexes for performance"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_threats_detected_at ON threats(detected_at)",
                "CREATE INDEX IF NOT EXISTS idx_threats_severity ON threats(severity)",
                "CREATE INDEX IF NOT EXISTS idx_threats_type ON threats(threat_type)",
                "CREATE INDEX IF NOT EXISTS idx_threats_status ON threats(status)",
                "CREATE INDEX IF NOT EXISTS idx_network_source_ip ON network_activity(source_ip)",
                "CREATE INDEX IF NOT EXISTS idx_network_recorded_at ON network_activity(recorded_at)",
                "CREATE INDEX IF NOT EXISTS idx_file_path ON file_integrity(file_path)",
                "CREATE INDEX IF NOT EXISTS idx_file_monitored_at ON file_integrity(monitored_at)",
                "CREATE INDEX IF NOT EXISTS idx_process_recorded_at ON process_activity(recorded_at)",
                "CREATE INDEX IF NOT EXISTS idx_process_name ON process_activity(process_name)",
                "CREATE INDEX IF NOT EXISTS idx_metrics_recorded_at ON system_metrics(recorded_at)",
                "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            self.return_connection(conn)
            
            self.logger.info("Database indexes created")
            
        except Exception as e:
            self.logger.error("Failed to create indexes: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
    
    def log_threat(self, threat_data):
        """Log security threat to database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO threats 
                (threat_id, threat_type, severity, source, target, description, 
                 metadata, risk_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                threat_data.get('threat_id'),
                threat_data.get('threat_type'),
                threat_data.get('severity'),
                threat_data.get('source'),
                threat_data.get('target'),
                threat_data.get('description'),
                json.dumps(threat_data.get('metadata', {})),
                threat_data.get('risk_score', 0)
            ))
            
            conn.commit()
            self.return_connection(conn)
            
            self.logger.debug("Threat logged: %s", threat_data.get('threat_id'))
            
        except Exception as e:
            self.logger.error("Failed to log threat: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
    
    def log_network_activity(self, activity_data):
        """Log network activity"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO network_activity 
                (source_ip, destination_ip, source_port, destination_port,
                 protocol, bytes_sent, bytes_received, connection_duration, flags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                activity_data.get('source_ip'),
                activity_data.get('destination_ip'),
                activity_data.get('source_port'),
                activity_data.get('destination_port'),
                activity_data.get('protocol'),
                activity_data.get('bytes_sent', 0),
                activity_data.get('bytes_received', 0),
                activity_data.get('duration', 0.0),
                activity_data.get('flags', '')
            ))
            
            conn.commit()
            self.return_connection(conn)
            
        except Exception as e:
            self.logger.error("Failed to log network activity: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
    
    def log_file_change(self, file_data):
        """Log file integrity change"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO file_integrity 
                (file_path, file_hash, file_size, last_modified, 
                 change_type, previous_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                file_data.get('file_path'),
                file_data.get('file_hash'),
                file_data.get('file_size'),
                file_data.get('last_modified'),
                file_data.get('change_type'),
                file_data.get('previous_hash')
            ))
            
            conn.commit()
            self.return_connection(conn)
            
        except Exception as e:
            self.logger.error("Failed to log file change: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
    
    def log_process_activity(self, process_data):
        """Log process activity"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO process_activity 
                (process_id, process_name, command_line, parent_pid,
                 cpu_percent, memory_percent, network_connections,
                 file_operations, user_name, start_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                process_data.get('process_id'),
                process_data.get('process_name'),
                process_data.get('command_line'),
                process_data.get('parent_pid'),
                process_data.get('cpu_percent', 0.0),
                process_data.get('memory_percent', 0.0),
                process_data.get('network_connections', 0),
                process_data.get('file_operations', 0),
                process_data.get('user_name'),
                process_data.get('start_time')
            ))
            
            conn.commit()
            self.return_connection(conn)
            
        except Exception as e:
            self.logger.error("Failed to log process activity: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
    
    def log_system_metrics(self, metrics_data):
        """Log system performance metrics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO system_metrics 
                (cpu_usage, memory_usage, disk_usage, network_in, network_out,
                 active_connections, running_processes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics_data.get('cpu_usage'),
                metrics_data.get('memory_usage'),
                metrics_data.get('disk_usage'),
                metrics_data.get('network_in'),
                metrics_data.get('network_out'),
                metrics_data.get('active_connections'),
                metrics_data.get('running_processes')
            ))
            
            conn.commit()
            self.return_connection(conn)
            
        except Exception as e:
            self.logger.error("Failed to log system metrics: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
    
    def log_audit_event(self, audit_data):
        """Log audit event"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_log 
                (user_id, action, resource, details, ip_address, 
                 user_agent, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_data.get('user_id'),
                audit_data.get('action'),
                audit_data.get('resource'),
                audit_data.get('details'),
                audit_data.get('ip_address'),
                audit_data.get('user_agent'),
                audit_data.get('status', 'success')
            ))
            
            conn.commit()
            self.return_connection(conn)
            
        except Exception as e:
            self.logger.error("Failed to log audit event: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
    
    def get_threat_statistics(self, days=30):
        """Get threat statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Threat count by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM threats 
                WHERE detected_at >= datetime('now', '-{} days')
                GROUP BY severity
            """.format(days))
            
            severity_stats = dict(cursor.fetchall())
            
            # Daily threat trends
            cursor.execute("""
                SELECT date(detected_at) as day, COUNT(*) as count
                FROM threats 
                WHERE detected_at >= datetime('now', '-{} days')
                GROUP BY date(detected_at)
                ORDER BY day
            """.format(days))
            
            daily_trends = cursor.fetchall()
            
            # Top threat types
            cursor.execute("""
                SELECT threat_type, COUNT(*) as count
                FROM threats 
                WHERE detected_at >= datetime('now', '-{} days')
                GROUP BY threat_type
                ORDER BY count DESC
                LIMIT 10
            """.format(days))
            
            top_types = cursor.fetchall()
            
            self.return_connection(conn)
            
            return {
                'severity_distribution': severity_stats,
                'daily_trends': daily_trends,
                'top_threat_types': top_types
            }
            
        except Exception as e:
            self.logger.error("Failed to get threat statistics: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
            return {}
    
    def get_network_statistics(self, hours=24):
        """Get network activity statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Top source IPs
            cursor.execute("""
                SELECT source_ip, COUNT(*) as connections,
                       SUM(bytes_sent + bytes_received) as total_bytes
                FROM network_activity 
                WHERE recorded_at >= datetime('now', '-{} hours')
                GROUP BY source_ip
                ORDER BY connections DESC
                LIMIT 10
            """.format(hours))
            
            top_sources = cursor.fetchall()
            
            # Protocol distribution
            cursor.execute("""
                SELECT protocol, COUNT(*) as count
                FROM network_activity 
                WHERE recorded_at >= datetime('now', '-{} hours')
                GROUP BY protocol
            """.format(hours))
            
            protocol_stats = cursor.fetchall()
            
            # Hourly activity
            cursor.execute("""
                SELECT strftime('%H', recorded_at) as hour, COUNT(*) as count
                FROM network_activity 
                WHERE recorded_at >= datetime('now', '-{} hours')
                GROUP BY strftime('%H', recorded_at)
                ORDER BY hour
            """.format(hours))
            
            hourly_activity = cursor.fetchall()
            
            self.return_connection(conn)
            
            return {
                'top_source_ips': top_sources,
                'protocol_distribution': protocol_stats,
                'hourly_activity': hourly_activity
            }
            
        except Exception as e:
            self.logger.error("Failed to get network statistics: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
            return {}
    
    def export_data(self, table_name, output_file, date_from=None, date_to=None):
        """Export table data to CSV"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build query with optional date filtering
            query = f"SELECT * FROM {table_name}"
            params = []
            
            if date_from or date_to:
                # Assume tables have a timestamp column
                timestamp_columns = {
                    'threats': 'detected_at',
                    'network_activity': 'recorded_at',
                    'file_integrity': 'monitored_at',
                    'process_activity': 'recorded_at',
                    'system_metrics': 'recorded_at',
                    'audit_log': 'timestamp'
                }
                
                timestamp_col = timestamp_columns.get(table_name)
                if timestamp_col:
                    conditions = []
                    if date_from:
                        conditions.append(f"{timestamp_col} >= ?")
                        params.append(date_from)
                    if date_to:
                        conditions.append(f"{timestamp_col} <= ?")
                        params.append(date_to)
                    
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)
            
            cursor.execute(query, params)
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Export to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                
                for row in cursor.fetchall():
                    writer.writerow(row)
            
            self.return_connection(conn)
            
            self.logger.info("Data exported to %s", output_file)
            return True
            
        except Exception as e:
            self.logger.error("Failed to export data: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
            return False
    
    def cleanup_old_data(self, days_to_keep=90):
        """Clean up old data to manage database size"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            # Clean up old records
            cleanup_queries = [
                f"DELETE FROM network_activity WHERE recorded_at < '{cutoff_date}'",
                f"DELETE FROM process_activity WHERE recorded_at < '{cutoff_date}'",
                f"DELETE FROM system_metrics WHERE recorded_at < '{cutoff_date}'",
                f"DELETE FROM file_integrity WHERE monitored_at < '{cutoff_date}'"
            ]
            
            total_deleted = 0
            for query in cleanup_queries:
                cursor.execute(query)
                total_deleted += cursor.rowcount
            
            # Vacuum database to reclaim space
            cursor.execute("VACUUM")
            
            conn.commit()
            self.return_connection(conn)
            
            self.logger.info("Cleaned up %d old records", total_deleted)
            return total_deleted
            
        except Exception as e:
            self.logger.error("Failed to cleanup old data: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
            return 0
    
    def get_database_info(self):
        """Get database information and statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get table sizes
            tables = [
                'threats', 'network_activity', 'file_integrity',
                'process_activity', 'system_metrics', 'audit_log'
            ]
            
            table_info = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_info[table] = count
            
            # Get database file size
            db_size = Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            
            self.return_connection(conn)
            
            return {
                'database_file': self.db_path,
                'database_size_mb': round(db_size / 1024 / 1024, 2),
                'table_counts': table_info,
                'total_records': sum(table_info.values())
            }
            
        except Exception as e:
            self.logger.error("Failed to get database info: %s", e)
            if 'conn' in locals():
                self.return_connection(conn)
            return {}


if __name__ == '__main__':
    # Test database integration
    db = DatabaseIntegration()
    
    # Test threat logging
    test_threat = {
        'threat_id': 'test_001',
        'threat_type': 'network_intrusion',
        'severity': 'high',
        'source': '192.168.1.100',
        'target': '192.168.1.1',
        'description': 'Suspicious network activity detected',
        'metadata': {'port': 22, 'protocol': 'ssh'},
        'risk_score': 75
    }
    
    db.log_threat(test_threat)
    
    # Get statistics
    stats = db.get_threat_statistics(30)
    print("Threat Statistics:", stats)
    
    # Get database info
    info = db.get_database_info()
    print("Database Info:", info)