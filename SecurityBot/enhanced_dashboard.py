"""
Security Bot Enterprise - Enhanced Dashboard
Real-time security monitoring dashboard with Chart.js visualizations
"""

import os
import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import logging


class EnhancedDashboard:
    """Enterprise security dashboard with real-time monitoring"""
    
    def __init__(self, port=8080, db_path="security_bot.db"):
        self.port = port
        self.db_path = db_path
        self.server = None
        self.running = False
        self.setup_logging()
        
    def setup_logging(self):
        """Setup dashboard logging"""
        self.logger = logging.getLogger('Dashboard')
    
    def start_server(self):
        """Start dashboard web server"""
        try:
            self.running = True
            self.logger.info("Starting dashboard server on port %d", self.port)
            
            handler = DashboardRequestHandler
            handler.dashboard = self
            
            self.server = HTTPServer(('127.0.0.1', self.port), handler)
            self.server.serve_forever()
            
        except Exception as e:
            self.logger.error("Dashboard server error: %s", e)
    
    def stop_server(self):
        """Stop dashboard server"""
        if self.server:
            self.running = False
            self.server.shutdown()
            self.logger.info("Dashboard server stopped")
    
    def get_dashboard_data(self):
        """Get dashboard data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get threat counts by severity
            cursor.execute("""
                SELECT severity, COUNT(*) 
                FROM threats 
                WHERE detected_at >= datetime('now', '-24 hours')
                GROUP BY severity
            """)
            severity_data = dict(cursor.fetchall())
            
            # Get recent threats
            cursor.execute("""
                SELECT threat_type, severity, detected_at, description
                FROM threats 
                ORDER BY detected_at DESC 
                LIMIT 10
            """)
            recent_threats = cursor.fetchall()
            
            # Get hourly threat distribution
            cursor.execute("""
                SELECT strftime('%H', detected_at) as hour, COUNT(*) 
                FROM threats 
                WHERE detected_at >= datetime('now', '-24 hours')
                GROUP BY hour
                ORDER BY hour
            """)
            hourly_data = cursor.fetchall()
            
            conn.close()
            
            return {
                'severity_distribution': severity_data,
                'recent_threats': recent_threats,
                'hourly_distribution': hourly_data,
                'total_threats_24h': sum(severity_data.values()),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error("Error getting dashboard data: %s", e)
            return {
                'severity_distribution': {},
                'recent_threats': [],
                'hourly_distribution': [],
                'total_threats_24h': 0,
                'last_updated': datetime.now().isoformat()
            }


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboard"""
    
    dashboard = None
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                self.serve_dashboard_html()
            elif self.path == '/api/dashboard-data':
                self.serve_dashboard_data()
            elif self.path.startswith('/static/'):
                self.serve_static_file()
            else:
                self.send_error(404)
                
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_dashboard_html(self):
        """Serve main dashboard HTML"""
        html = self.get_dashboard_html()
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(html.encode()))
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_dashboard_data(self):
        """Serve dashboard data as JSON"""
        if self.dashboard:
            data = self.dashboard.get_dashboard_data()
        else:
            data = {'error': 'Dashboard not available'}
        
        json_data = json.dumps(data).encode()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(json_data))
        self.end_headers()
        self.wfile.write(json_data)
    
    def serve_static_file(self):
        """Serve static files (CSS, JS)"""
        self.send_error(404)  # Simplified for now
    
    def get_dashboard_html(self):
        """Generate dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Bot Enterprise - Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(0,0,0,0.1);
            color: white;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        .metric {
            text-align: center;
            padding: 20px;
        }
        
        .metric-value {
            font-size: 36px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 10px;
        }
        
        .metric-label {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .threat-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .threat-item {
            padding: 10px;
            margin: 5px 0;
            border-left: 4px solid #3498db;
            background: #f8f9fa;
            border-radius: 4px;
        }
        
        .threat-item.critical {
            border-left-color: #e74c3c;
        }
        
        .threat-item.high {
            border-left-color: #f39c12;
        }
        
        .threat-item.medium {
            border-left-color: #f1c40f;
        }
        
        .threat-item.low {
            border-left-color: #27ae60;
        }
        
        .threat-type {
            font-weight: bold;
            color: #2c3e50;
        }
        
        .threat-time {
            font-size: 12px;
            color: #7f8c8d;
            float: right;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online {
            background: #27ae60;
            box-shadow: 0 0 10px rgba(39, 174, 96, 0.5);
        }
        
        .auto-refresh {
            text-align: center;
            margin-top: 20px;
            color: white;
            font-size: 14px;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Security Bot Enterprise</h1>
        <p>Real-time Security Monitoring Dashboard</p>
        <p><span class="status-indicator status-online"></span>System Online</p>
    </div>
    
    <div class="container">
        <div class="dashboard-grid">
            <!-- Total Threats Card -->
            <div class="card">
                <div class="metric">
                    <div class="metric-value" id="totalThreats">--</div>
                    <div class="metric-label">Threats (24h)</div>
                </div>
            </div>
            
            <!-- System Status Card -->
            <div class="card">
                <div class="metric">
                    <div class="metric-value" style="color: #27ae60;">ACTIVE</div>
                    <div class="metric-label">Monitoring Status</div>
                </div>
            </div>
            
            <!-- Last Update Card -->
            <div class="card">
                <div class="metric">
                    <div class="metric-value" id="lastUpdate" style="font-size: 18px;">--</div>
                    <div class="metric-label">Last Updated</div>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <!-- Threat Distribution Chart -->
            <div class="card">
                <h3>📊 Threat Distribution by Severity</h3>
                <div class="chart-container">
                    <canvas id="severityChart"></canvas>
                </div>
            </div>
            
            <!-- Hourly Activity Chart -->
            <div class="card">
                <h3>⏰ Hourly Threat Activity</h3>
                <div class="chart-container">
                    <canvas id="hourlyChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Recent Threats -->
        <div class="card">
            <h3>🚨 Recent Threats</h3>
            <div class="threat-list" id="threatList">
                <!-- Threats will be populated here -->
            </div>
        </div>
        
        <div class="auto-refresh">
            Dashboard updates automatically every 30 seconds
        </div>
    </div>
    
    <script>
        let severityChart = null;
        let hourlyChart = null;
        
        // Initialize charts
        function initCharts() {
            // Severity distribution chart
            const severityCtx = document.getElementById('severityChart').getContext('2d');
            severityChart = new Chart(severityCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#e74c3c', '#f39c12', '#f1c40f', '#27ae60'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
            
            // Hourly activity chart
            const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
            hourlyChart = new Chart(hourlyCtx, {
                type: 'line',
                data: {
                    labels: Array.from({length: 24}, (_, i) => i.toString().padStart(2, '0') + ':00'),
                    datasets: [{
                        label: 'Threats Detected',
                        data: new Array(24).fill(0),
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Update dashboard data
        function updateDashboard() {
            fetch('/api/dashboard-data')
                .then(response => response.json())
                .then(data => {
                    // Update metrics
                    document.getElementById('totalThreats').textContent = data.total_threats_24h || 0;
                    document.getElementById('lastUpdate').textContent = new Date(data.last_updated).toLocaleTimeString();
                    
                    // Update severity chart
                    if (severityChart) {
                        const severityData = data.severity_distribution || {};
                        severityChart.data.datasets[0].data = [
                            severityData.critical || 0,
                            severityData.high || 0,
                            severityData.medium || 0,
                            severityData.low || 0
                        ];
                        severityChart.update();
                    }
                    
                    // Update hourly chart
                    if (hourlyChart) {
                        const hourlyData = new Array(24).fill(0);
                        if (data.hourly_distribution) {
                            data.hourly_distribution.forEach(([hour, count]) => {
                                hourlyData[parseInt(hour)] = count;
                            });
                        }
                        hourlyChart.data.datasets[0].data = hourlyData;
                        hourlyChart.update();
                    }
                    
                    // Update recent threats
                    updateThreatList(data.recent_threats || []);
                })
                .catch(error => {
                    console.error('Error updating dashboard:', error);
                });
        }
        
        // Update threat list
        function updateThreatList(threats) {
            const threatList = document.getElementById('threatList');
            
            if (threats.length === 0) {
                threatList.innerHTML = '<div style="text-align: center; color: #7f8c8d; padding: 20px;">No recent threats detected</div>';
                return;
            }
            
            threatList.innerHTML = threats.map(threat => {
                const [type, severity, timestamp, description] = threat;
                const time = new Date(timestamp).toLocaleString();
                
                return `
                    <div class="threat-item ${severity}">
                        <span class="threat-type">${type.replace(/_/g, ' ').toUpperCase()}</span>
                        <span class="threat-time">${time}</span>
                        <div style="margin-top: 5px; font-size: 14px;">${description || 'No description available'}</div>
                    </div>
                `;
            }).join('');
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            updateDashboard();
            
            // Auto-refresh every 30 seconds
            setInterval(updateDashboard, 30000);
        });
    </script>
</body>
</html>
        """


if __name__ == '__main__':
    dashboard = EnhancedDashboard()
    dashboard.start_server()