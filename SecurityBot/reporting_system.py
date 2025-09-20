"""
Security Bot Enterprise - Reporting System
Automated PDF report generation with security analytics
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import io
import base64


class ReportingSystem:
    """Enterprise reporting system with PDF generation"""
    
    def __init__(self, db_path="security_bot.db", output_dir="reports"):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup reporting logging"""
        self.logger = logging.getLogger('ReportingSystem')
    
    def generate_threat_summary_report(self, days=30, format_type='html'):
        """Generate threat summary report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Total threats by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM threats 
                WHERE detected_at >= ? AND detected_at <= ?
                GROUP BY severity
                ORDER BY count DESC
            """, (start_date.isoformat(), end_date.isoformat()))
            
            severity_data = cursor.fetchall()
            
            # Daily threat trends
            cursor.execute("""
                SELECT DATE(detected_at) as date, COUNT(*) as count
                FROM threats 
                WHERE detected_at >= ? AND detected_at <= ?
                GROUP BY DATE(detected_at)
                ORDER BY date
            """, (start_date.isoformat(), end_date.isoformat()))
            
            daily_trends = cursor.fetchall()
            
            # Top threat types
            cursor.execute("""
                SELECT threat_type, COUNT(*) as count, 
                       AVG(risk_score) as avg_risk_score
                FROM threats 
                WHERE detected_at >= ? AND detected_at <= ?
                GROUP BY threat_type
                ORDER BY count DESC
                LIMIT 10
            """, (start_date.isoformat(), end_date.isoformat()))
            
            threat_types = cursor.fetchall()
            
            # Recent critical threats
            cursor.execute("""
                SELECT threat_id, threat_type, source, target, 
                       description, detected_at, risk_score
                FROM threats 
                WHERE severity = 'critical' 
                AND detected_at >= ? AND detected_at <= ?
                ORDER BY detected_at DESC
                LIMIT 10
            """, (start_date.isoformat(), end_date.isoformat()))
            
            critical_threats = cursor.fetchall()
            
            conn.close()
            
            # Generate report data
            report_data = {
                'title': 'Security Threat Summary Report',
                'period': f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}',
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_threats': sum([row[1] for row in severity_data]),
                    'critical_threats': next((row[1] for row in severity_data if row[0] == 'critical'), 0),
                    'days_analyzed': days
                },
                'severity_distribution': severity_data,
                'daily_trends': daily_trends,
                'top_threat_types': threat_types,
                'critical_threats': critical_threats
            }
            
            # Generate report based on format
            if format_type.lower() == 'html':
                return self._generate_html_report(report_data)
            elif format_type.lower() == 'json':
                return self._generate_json_report(report_data)
            else:
                return self._generate_text_report(report_data)
                
        except Exception as e:
            self.logger.error("Failed to generate threat summary report: %s", e)
            return None
    
    def generate_network_activity_report(self, hours=24, format_type='html'):
        """Generate network activity report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get date range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Total network activity
            cursor.execute("""
                SELECT COUNT(*) as total_connections,
                       SUM(bytes_sent + bytes_received) as total_bytes,
                       AVG(connection_duration) as avg_duration
                FROM network_activity 
                WHERE recorded_at >= ? AND recorded_at <= ?
            """, (start_time.isoformat(), end_time.isoformat()))
            
            activity_summary = cursor.fetchone()
            
            # Top source IPs
            cursor.execute("""
                SELECT source_ip, COUNT(*) as connections,
                       SUM(bytes_sent + bytes_received) as total_bytes
                FROM network_activity 
                WHERE recorded_at >= ? AND recorded_at <= ?
                GROUP BY source_ip
                ORDER BY connections DESC
                LIMIT 10
            """, (start_time.isoformat(), end_time.isoformat()))
            
            top_sources = cursor.fetchall()
            
            # Protocol distribution
            cursor.execute("""
                SELECT protocol, COUNT(*) as count,
                       SUM(bytes_sent + bytes_received) as total_bytes
                FROM network_activity 
                WHERE recorded_at >= ? AND recorded_at <= ?
                GROUP BY protocol
                ORDER BY count DESC
            """, (start_time.isoformat(), end_time.isoformat()))
            
            protocol_stats = cursor.fetchall()
            
            # Hourly activity pattern
            cursor.execute("""
                SELECT strftime('%H', recorded_at) as hour, 
                       COUNT(*) as connections
                FROM network_activity 
                WHERE recorded_at >= ? AND recorded_at <= ?
                GROUP BY strftime('%H', recorded_at)
                ORDER BY hour
            """, (start_time.isoformat(), end_time.isoformat()))
            
            hourly_pattern = cursor.fetchall()
            
            conn.close()
            
            # Generate report data
            report_data = {
                'title': 'Network Activity Report',
                'period': f'{start_time.strftime("%Y-%m-%d %H:%M")} to {end_time.strftime("%Y-%m-%d %H:%M")}',
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_connections': activity_summary[0] or 0,
                    'total_bytes': activity_summary[1] or 0,
                    'average_duration': round(activity_summary[2] or 0, 2),
                    'hours_analyzed': hours
                },
                'top_source_ips': top_sources,
                'protocol_distribution': protocol_stats,
                'hourly_pattern': hourly_pattern
            }
            
            # Generate report based on format
            if format_type.lower() == 'html':
                return self._generate_network_html_report(report_data)
            elif format_type.lower() == 'json':
                return self._generate_json_report(report_data)
            else:
                return self._generate_text_report(report_data)
                
        except Exception as e:
            self.logger.error("Failed to generate network activity report: %s", e)
            return None
    
    def generate_system_health_report(self, hours=24, format_type='html'):
        """Generate system health report"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get date range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # System metrics summary
            cursor.execute("""
                SELECT AVG(cpu_usage) as avg_cpu,
                       MAX(cpu_usage) as max_cpu,
                       AVG(memory_usage) as avg_memory,
                       MAX(memory_usage) as max_memory,
                       AVG(disk_usage) as avg_disk,
                       COUNT(*) as data_points
                FROM system_metrics 
                WHERE recorded_at >= ? AND recorded_at <= ?
            """, (start_time.isoformat(), end_time.isoformat()))
            
            metrics_summary = cursor.fetchone()
            
            # Resource usage trends
            cursor.execute("""
                SELECT strftime('%H', recorded_at) as hour,
                       AVG(cpu_usage) as avg_cpu,
                       AVG(memory_usage) as avg_memory,
                       AVG(disk_usage) as avg_disk
                FROM system_metrics 
                WHERE recorded_at >= ? AND recorded_at <= ?
                GROUP BY strftime('%H', recorded_at)
                ORDER BY hour
            """, (start_time.isoformat(), end_time.isoformat()))
            
            hourly_metrics = cursor.fetchall()
            
            # Alert history
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM alert_history 
                WHERE created_at >= ? AND created_at <= ?
                GROUP BY status
            """, (start_time.isoformat(), end_time.isoformat()))
            
            alert_stats = cursor.fetchall()
            
            conn.close()
            
            # Generate report data
            report_data = {
                'title': 'System Health Report',
                'period': f'{start_time.strftime("%Y-%m-%d %H:%M")} to {end_time.strftime("%Y-%m-%d %H:%M")}',
                'generated_at': datetime.now().isoformat(),
                'summary': {
                    'avg_cpu_usage': round(metrics_summary[0] or 0, 2),
                    'max_cpu_usage': round(metrics_summary[1] or 0, 2),
                    'avg_memory_usage': round(metrics_summary[2] or 0, 2),
                    'max_memory_usage': round(metrics_summary[3] or 0, 2),
                    'avg_disk_usage': round(metrics_summary[4] or 0, 2),
                    'data_points': metrics_summary[5] or 0,
                    'hours_analyzed': hours
                },
                'hourly_metrics': hourly_metrics,
                'alert_statistics': alert_stats
            }
            
            # Generate report based on format
            if format_type.lower() == 'html':
                return self._generate_health_html_report(report_data)
            elif format_type.lower() == 'json':
                return self._generate_json_report(report_data)
            else:
                return self._generate_text_report(report_data)
                
        except Exception as e:
            self.logger.error("Failed to generate system health report: %s", e)
            return None
    
    def _generate_html_report(self, report_data):
        """Generate HTML threat summary report"""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0 0 10px 0;
        }}
        .header p {{
            color: #7f8c8d;
            margin: 5px 0;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .summary-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .section {{
            margin: 30px 0;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 1px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
            color: #2c3e50;
        }}
        .severity-critical {{ color: #e74c3c; font-weight: bold; }}
        .severity-high {{ color: #f39c12; font-weight: bold; }}
        .severity-medium {{ color: #f1c40f; font-weight: bold; }}
        .severity-low {{ color: #27ae60; font-weight: bold; }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ {title}</h1>
            <p><strong>Period:</strong> {period}</p>
            <p><strong>Generated:</strong> {generated_at}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-value">{total_threats}</div>
                <div class="summary-label">Total Threats</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{critical_threats}</div>
                <div class="summary-label">Critical Threats</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{days_analyzed}</div>
                <div class="summary-label">Days Analyzed</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Threat Distribution by Severity</h2>
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {severity_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>🔍 Top Threat Types</h2>
            <table>
                <thead>
                    <tr>
                        <th>Threat Type</th>
                        <th>Count</th>
                        <th>Average Risk Score</th>
                    </tr>
                </thead>
                <tbody>
                    {threat_type_rows}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>🚨 Recent Critical Threats</h2>
            <table>
                <thead>
                    <tr>
                        <th>Threat ID</th>
                        <th>Type</th>
                        <th>Source</th>
                        <th>Target</th>
                        <th>Detected At</th>
                        <th>Risk Score</th>
                    </tr>
                </thead>
                <tbody>
                    {critical_threat_rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Report generated by Security Bot Enterprise</p>
            <p>For more information, contact your security administrator</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Calculate total for percentages
        total_threats = report_data['summary']['total_threats']
        
        # Generate severity rows
        severity_rows = ""
        for severity, count in report_data['severity_distribution']:
            percentage = (count / total_threats * 100) if total_threats > 0 else 0
            severity_class = f"severity-{severity}"
            severity_rows += f"""
                <tr>
                    <td><span class="{severity_class}">{severity.upper()}</span></td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            """
        
        # Generate threat type rows
        threat_type_rows = ""
        for threat_type, count, avg_risk in report_data['top_threat_types']:
            threat_type_rows += f"""
                <tr>
                    <td>{threat_type.replace('_', ' ').title()}</td>
                    <td>{count}</td>
                    <td>{avg_risk:.1f}</td>
                </tr>
            """
        
        # Generate critical threat rows
        critical_threat_rows = ""
        for threat in report_data['critical_threats']:
            threat_id, threat_type, source, target, detected_at, risk_score = threat
            detected_time = datetime.fromisoformat(detected_at).strftime('%Y-%m-%d %H:%M')
            critical_threat_rows += f"""
                <tr>
                    <td>{threat_id}</td>
                    <td>{threat_type.replace('_', ' ').title()}</td>
                    <td>{source or 'N/A'}</td>
                    <td>{target or 'N/A'}</td>
                    <td>{detected_time}</td>
                    <td>{risk_score}</td>
                </tr>
            """
        
        # Fill template
        html_content = html_template.format(
            title=report_data['title'],
            period=report_data['period'],
            generated_at=datetime.fromisoformat(report_data['generated_at']).strftime('%Y-%m-%d %H:%M:%S'),
            total_threats=report_data['summary']['total_threats'],
            critical_threats=report_data['summary']['critical_threats'],
            days_analyzed=report_data['summary']['days_analyzed'],
            severity_rows=severity_rows,
            threat_type_rows=threat_type_rows,
            critical_threat_rows=critical_threat_rows
        )
        
        return html_content
    
    def _generate_network_html_report(self, report_data):
        """Generate HTML network activity report"""
        # Simplified network HTML report
        return f"""
        <html>
        <head><title>{report_data['title']}</title></head>
        <body>
            <h1>{report_data['title']}</h1>
            <p>Period: {report_data['period']}</p>
            <h2>Summary</h2>
            <p>Total Connections: {report_data['summary']['total_connections']}</p>
            <p>Total Bytes: {report_data['summary']['total_bytes']}</p>
            <p>Average Duration: {report_data['summary']['average_duration']} seconds</p>
        </body>
        </html>
        """
    
    def _generate_health_html_report(self, report_data):
        """Generate HTML system health report"""
        # Simplified health HTML report
        return f"""
        <html>
        <head><title>{report_data['title']}</title></head>
        <body>
            <h1>{report_data['title']}</h1>
            <p>Period: {report_data['period']}</p>
            <h2>System Metrics</h2>
            <p>Average CPU Usage: {report_data['summary']['avg_cpu_usage']}%</p>
            <p>Average Memory Usage: {report_data['summary']['avg_memory_usage']}%</p>
            <p>Average Disk Usage: {report_data['summary']['avg_disk_usage']}%</p>
        </body>
        </html>
        """
    
    def _generate_json_report(self, report_data):
        """Generate JSON report"""
        return json.dumps(report_data, indent=2, default=str)
    
    def _generate_text_report(self, report_data):
        """Generate plain text report"""
        text_lines = [
            f"=== {report_data['title']} ===",
            f"Period: {report_data['period']}",
            f"Generated: {report_data['generated_at']}",
            "",
            "SUMMARY:",
        ]
        
        for key, value in report_data['summary'].items():
            text_lines.append(f"  {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(text_lines)
    
    def save_report(self, report_content, filename):
        """Save report to file"""
        try:
            output_path = self.output_dir / filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info("Report saved to %s", output_path)
            return str(output_path)
            
        except Exception as e:
            self.logger.error("Failed to save report: %s", e)
            return None
    
    def schedule_reports(self):
        """Schedule automatic report generation"""
        # This would be implemented with a scheduler like APScheduler
        # For now, just log the intention
        self.logger.info("Report scheduling would be implemented here")


if __name__ == '__main__':
    # Test reporting system
    reporting = ReportingSystem()
    
    # Generate threat summary report
    report = reporting.generate_threat_summary_report(30, 'html')
    if report:
        filename = f"threat_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        output_path = reporting.save_report(report, filename)
        print(f"Report generated: {output_path}")
    else:
        print("Failed to generate report")