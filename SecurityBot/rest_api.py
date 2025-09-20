"""
Security Bot Enterprise - REST API
Flask-based REST API for system integration and management
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import jwt
import json
import logging
from datetime import datetime
import sqlite3
from functools import wraps
import os
import tempfile


class SecurityBotAPI:
    """Enterprise REST API for Security Bot"""
    
    def __init__(self, auth_system, db_integration, threat_detection, 
                 alerting_system, port=5000):
        self.app = Flask(__name__)
        CORS(self.app)
        
        self.auth_system = auth_system
        self.db_integration = db_integration
        self.threat_detection = threat_detection
        self.alerting_system = alerting_system
        self.port = port
        
        self.setup_logging()
        self.setup_routes()
    
    def setup_logging(self):
        """Setup API logging"""
        self.logger = logging.getLogger('SecurityBotAPI')
        
        # Configure Flask logging
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    def require_auth(self, permission=None):
        """Authentication decorator"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                token = None
                
                # Get token from header
                if 'Authorization' in request.headers:
                    auth_header = request.headers['Authorization']
                    if auth_header.startswith('Bearer '):
                        token = auth_header.split(' ')[1]
                
                if not token:
                    return jsonify({'error': 'Authentication required'}), 401
                
                # Verify token
                auth_result = self.auth_system.verify_token(token)
                if not auth_result['success']:
                    return jsonify({'error': auth_result['message']}), 401
                
                # Check permission
                if permission:
                    if not self.auth_system.check_permission(
                        auth_result['role'], permission
                    ):
                        return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Add user info to request
                request.current_user = auth_result
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def setup_routes(self):
        """Setup API routes"""
        
        # Health check
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        
        # Authentication endpoints
        @self.app.route('/auth/login', methods=['POST'])
        def login():
            data = request.get_json()
            
            if not data or 'username' not in data or 'password' not in data:
                return jsonify({'error': 'Username and password required'}), 400
            
            result = self.auth_system.login(data['username'], data['password'])
            
            if result['success']:
                return jsonify({
                    'token': result['token'],
                    'user': result['user']
                })
            else:
                return jsonify({'error': result['message']}), 401
        
        @self.app.route('/auth/logout', methods=['POST'])
        @self.require_auth()
        def logout():
            token = request.headers['Authorization'].split(' ')[1]
            result = self.auth_system.logout(token)
            
            if result['success']:
                return jsonify({'message': 'Logged out successfully'})
            else:
                return jsonify({'error': result['message']}), 400
        
        @self.app.route('/auth/user', methods=['GET'])
        @self.require_auth()
        def get_current_user():
            return jsonify(request.current_user)
        
        # Threat management endpoints
        @self.app.route('/threats', methods=['GET'])
        @self.require_auth('read')
        def get_threats():
            try:
                page = int(request.args.get('page', 1))
                limit = min(int(request.args.get('limit', 50)), 100)
                severity = request.args.get('severity')
                status = request.args.get('status')
                
                offset = (page - 1) * limit
                
                # Build query
                query = "SELECT * FROM threats WHERE 1=1"
                params = []
                
                if severity:
                    query += " AND severity = ?"
                    params.append(severity)
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                query += " ORDER BY detected_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                # Execute query
                conn = self.db_integration.get_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                threats = []
                for row in cursor.fetchall():
                    threat = dict(row)
                    if threat['metadata']:
                        threat['metadata'] = json.loads(threat['metadata'])
                    threats.append(threat)
                
                # Get total count
                count_query = "SELECT COUNT(*) FROM threats WHERE 1=1"
                count_params = []
                
                if severity:
                    count_query += " AND severity = ?"
                    count_params.append(severity)
                
                if status:
                    count_query += " AND status = ?"
                    count_params.append(status)
                
                cursor.execute(count_query, count_params)
                total = cursor.fetchone()[0]
                
                self.db_integration.return_connection(conn)
                
                return jsonify({
                    'threats': threats,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total,
                        'pages': (total + limit - 1) // limit
                    }
                })
                
            except Exception as e:
                self.logger.error("Failed to get threats: %s", e)
                return jsonify({'error': 'Failed to retrieve threats'}), 500
        
        @self.app.route('/threats/<threat_id>', methods=['GET'])
        @self.require_auth('read')
        def get_threat(threat_id):
            try:
                conn = self.db_integration.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM threats WHERE threat_id = ?", (threat_id,))
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'error': 'Threat not found'}), 404
                
                threat = dict(row)
                if threat['metadata']:
                    threat['metadata'] = json.loads(threat['metadata'])
                
                self.db_integration.return_connection(conn)
                
                return jsonify(threat)
                
            except Exception as e:
                self.logger.error("Failed to get threat: %s", e)
                return jsonify({'error': 'Failed to retrieve threat'}), 500
        
        @self.app.route('/threats/<threat_id>/status', methods=['PUT'])
        @self.require_auth('write')
        def update_threat_status(threat_id):
            try:
                data = request.get_json()
                if 'status' not in data:
                    return jsonify({'error': 'Status required'}), 400
                
                conn = self.db_integration.get_connection()
                cursor = conn.cursor()
                
                # Update threat status
                cursor.execute("""
                    UPDATE threats 
                    SET status = ?, resolved_at = CASE 
                        WHEN ? = 'resolved' THEN CURRENT_TIMESTAMP 
                        ELSE resolved_at 
                    END
                    WHERE threat_id = ?
                """, (data['status'], data['status'], threat_id))
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Threat not found'}), 404
                
                conn.commit()
                self.db_integration.return_connection(conn)
                
                # Log audit event
                self.db_integration.log_audit_event({
                    'user_id': request.current_user['username'],
                    'action': 'update_threat_status',
                    'resource': f'threat/{threat_id}',
                    'details': f"Status changed to {data['status']}",
                    'ip_address': request.remote_addr
                })
                
                return jsonify({'message': 'Threat status updated'})
                
            except Exception as e:
                self.logger.error("Failed to update threat status: %s", e)
                return jsonify({'error': 'Failed to update threat status'}), 500
        
        # Statistics endpoints
        @self.app.route('/statistics/threats', methods=['GET'])
        @self.require_auth('read')
        def get_threat_statistics():
            try:
                days = int(request.args.get('days', 30))
                stats = self.db_integration.get_threat_statistics(days)
                return jsonify(stats)
                
            except Exception as e:
                self.logger.error("Failed to get threat statistics: %s", e)
                return jsonify({'error': 'Failed to retrieve statistics'}), 500
        
        @self.app.route('/statistics/network', methods=['GET'])
        @self.require_auth('read')
        def get_network_statistics():
            try:
                hours = int(request.args.get('hours', 24))
                stats = self.db_integration.get_network_statistics(hours)
                return jsonify(stats)
                
            except Exception as e:
                self.logger.error("Failed to get network statistics: %s", e)
                return jsonify({'error': 'Failed to retrieve statistics'}), 500
        
        @self.app.route('/statistics/system', methods=['GET'])
        @self.require_auth('read')
        def get_system_statistics():
            try:
                # Get latest system metrics
                conn = self.db_integration.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM system_metrics 
                    ORDER BY recorded_at DESC 
                    LIMIT 1
                """)
                
                latest_metrics = cursor.fetchone()
                
                # Get average metrics for the last hour
                cursor.execute("""
                    SELECT 
                        AVG(cpu_usage) as avg_cpu,
                        AVG(memory_usage) as avg_memory,
                        AVG(disk_usage) as avg_disk,
                        AVG(network_in) as avg_network_in,
                        AVG(network_out) as avg_network_out
                    FROM system_metrics 
                    WHERE recorded_at >= datetime('now', '-1 hour')
                """)
                
                avg_metrics = cursor.fetchone()
                
                self.db_integration.return_connection(conn)
                
                return jsonify({
                    'current': dict(latest_metrics) if latest_metrics else {},
                    'hourly_average': dict(avg_metrics) if avg_metrics else {}
                })
                
            except Exception as e:
                self.logger.error("Failed to get system statistics: %s", e)
                return jsonify({'error': 'Failed to retrieve statistics'}), 500
        
        # Alerting endpoints
        @self.app.route('/alerts', methods=['POST'])
        @self.require_auth('write')
        def create_alert():
            try:
                data = request.get_json()
                
                required_fields = ['alert_id', 'severity', 'title', 'message']
                if not all(field in data for field in required_fields):
                    return jsonify({'error': 'Missing required fields'}), 400
                
                self.alerting_system.create_alert(
                    data['alert_id'],
                    data['severity'],
                    data['title'],
                    data['message'],
                    data.get('metadata')
                )
                
                return jsonify({'message': 'Alert created successfully'})
                
            except Exception as e:
                self.logger.error("Failed to create alert: %s", e)
                return jsonify({'error': 'Failed to create alert'}), 500
        
        @self.app.route('/alerts/test', methods=['POST'])
        @self.require_auth('admin')
        def test_alerts():
            try:
                self.alerting_system.test_channels()
                return jsonify({'message': 'Test alerts sent'})
                
            except Exception as e:
                self.logger.error("Failed to send test alerts: %s", e)
                return jsonify({'error': 'Failed to send test alerts'}), 500
        
        # Export endpoints
        @self.app.route('/export/<table_name>', methods=['GET'])
        @self.require_auth('read')
        def export_data(table_name):
            try:
                # Validate table name
                valid_tables = [
                    'threats', 'network_activity', 'file_integrity',
                    'process_activity', 'system_metrics', 'audit_log'
                ]
                
                if table_name not in valid_tables:
                    return jsonify({'error': 'Invalid table name'}), 400
                
                # Get date parameters
                date_from = request.args.get('date_from')
                date_to = request.args.get('date_to')
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    mode='w', 
                    suffix='.csv', 
                    delete=False
                )
                temp_file.close()
                
                # Export data
                success = self.db_integration.export_data(
                    table_name, 
                    temp_file.name, 
                    date_from, 
                    date_to
                )
                
                if not success:
                    os.unlink(temp_file.name)
                    return jsonify({'error': 'Export failed'}), 500
                
                # Return file
                return send_file(
                    temp_file.name,
                    as_attachment=True,
                    download_name=f'{table_name}_export.csv',
                    mimetype='text/csv'
                )
                
            except Exception as e:
                self.logger.error("Failed to export data: %s", e)
                return jsonify({'error': 'Export failed'}), 500
        
        # System management endpoints
        @self.app.route('/system/info', methods=['GET'])
        @self.require_auth('read')
        def get_system_info():
            try:
                db_info = self.db_integration.get_database_info()
                
                return jsonify({
                    'database': db_info,
                    'api_version': '1.0.0',
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self.logger.error("Failed to get system info: %s", e)
                return jsonify({'error': 'Failed to retrieve system info'}), 500
        
        @self.app.route('/system/cleanup', methods=['POST'])
        @self.require_auth('admin')
        def cleanup_database():
            try:
                data = request.get_json() or {}
                days_to_keep = data.get('days_to_keep', 90)
                
                deleted_records = self.db_integration.cleanup_old_data(days_to_keep)
                
                # Log audit event
                self.db_integration.log_audit_event({
                    'user_id': request.current_user['username'],
                    'action': 'database_cleanup',
                    'resource': 'system',
                    'details': f"Cleaned up {deleted_records} old records",
                    'ip_address': request.remote_addr
                })
                
                return jsonify({
                    'message': f'Cleaned up {deleted_records} old records'
                })
                
            except Exception as e:
                self.logger.error("Failed to cleanup database: %s", e)
                return jsonify({'error': 'Database cleanup failed'}), 500
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500
    
    def run(self, debug=False):
        """Run the API server"""
        self.logger.info("Starting Security Bot API on port %d", self.port)
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)


if __name__ == '__main__':
    # This would normally be imported from other modules
    from auth_system import AuthenticationSystem
    from database_integration import DatabaseIntegration
    from threat_detection import ThreatDetectionEngine
    from alerting_system import AlertingSystem
    
    # Initialize components
    auth = AuthenticationSystem()
    db = DatabaseIntegration()
    threat_detection = ThreatDetectionEngine(db)
    alerting = AlertingSystem()
    
    # Start API
    api = SecurityBotAPI(auth, db, threat_detection, alerting)
    api.run(debug=True)