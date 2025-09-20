"""
Security Bot Enterprise - Alerting System
Multi-channel notification system for security alerts
"""

import smtplib
import json
import logging
import sqlite3
import threading
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests


class AlertingSystem:
    """Enterprise alerting with multiple notification channels"""
    
    def __init__(self, config_path="alerting_config.json", db_path="security_bot.db"):
        self.config_path = config_path
        self.db_path = db_path
        self.setup_logging()  # Setup logging first
        self.config = self.load_config()
        self.alert_queue = []
        self.queue_lock = threading.Lock()
        self.running = False
        self.init_alerting_database()
    
    def setup_logging(self):
        """Setup alerting logging"""
        self.logger = logging.getLogger('AlertingSystem')
    
    def load_config(self):
        """Load alerting configuration"""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "",
                "to_addresses": []
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#security-alerts"
            },
            "teams": {
                "enabled": False,
                "webhook_url": ""
            },
            "discord": {
                "enabled": False,
                "webhook_url": ""
            },
            "alert_rules": {
                "critical": {
                    "channels": ["email", "slack", "teams"],
                    "immediate": True
                },
                "high": {
                    "channels": ["email", "slack"],
                    "immediate": True
                },
                "medium": {
                    "channels": ["slack"],
                    "immediate": False,
                    "batch_interval": 300
                },
                "low": {
                    "channels": ["slack"],
                    "immediate": False,
                    "batch_interval": 900
                }
            }
        }
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return {**default_config, **config}
        except FileNotFoundError:
            self.save_config(default_config)
            return default_config
        except Exception as e:
            self.logger.error("Failed to load config: %s", e)
            return default_config
    
    def save_config(self, config=None):
        """Save alerting configuration"""
        try:
            config = config or self.config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            self.logger.info("Configuration saved")
        except Exception as e:
            self.logger.error("Failed to save config: %s", e)
    
    def init_alerting_database(self):
        """Initialize alerting database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Alert history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT,
                    channels TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP,
                    error_message TEXT
                )
            """)
            
            # Alert templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alert_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    template_type TEXT NOT NULL,
                    subject_template TEXT,
                    body_template TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Default templates
            default_templates = [
                (
                    "security_threat",
                    "email",
                    "🚨 Security Alert: {threat_type}",
                    """
                    <html>
                    <body>
                        <h2 style="color: #e74c3c;">Security Alert Detected</h2>
                        <p><strong>Threat Type:</strong> {threat_type}</p>
                        <p><strong>Severity:</strong> {severity}</p>
                        <p><strong>Detected At:</strong> {timestamp}</p>
                        <p><strong>Description:</strong> {description}</p>
                        <p><strong>Source:</strong> {source}</p>
                        
                        <h3>Recommended Actions:</h3>
                        <ul>
                            <li>Review the threat details immediately</li>
                            <li>Check system logs for related activities</li>
                            <li>Consider isolating affected systems if necessary</li>
                        </ul>
                        
                        <p style="color: #7f8c8d; font-size: 12px;">
                            This alert was generated by Security Bot Enterprise
                        </p>
                    </body>
                    </html>
                    """
                ),
                (
                    "system_status",
                    "slack",
                    "",
                    """
                    🛡️ *Security Bot Status Update*
                    
                    *Status:* {status}
                    *Component:* {component}
                    *Message:* {message}
                    *Timestamp:* {timestamp}
                    """
                )
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO alert_templates 
                (name, template_type, subject_template, body_template)
                VALUES (?, ?, ?, ?)
            """, default_templates)
            
            conn.commit()
            conn.close()
            
            self.logger.info("Alerting database initialized")
            
        except Exception as e:
            self.logger.error("Failed to initialize alerting database: %s", e)
    
    def start_processor(self):
        """Start alert processing thread"""
        if not self.running:
            self.running = True
            processor_thread = threading.Thread(target=self._process_alerts)
            processor_thread.daemon = True
            processor_thread.start()
            self.logger.info("Alert processor started")
    
    def stop_processor(self):
        """Stop alert processing"""
        self.running = False
        self.logger.info("Alert processor stopped")
    
    def _process_alerts(self):
        """Process alerts from queue"""
        while self.running:
            try:
                with self.queue_lock:
                    if self.alert_queue:
                        alert = self.alert_queue.pop(0)
                        self._send_alert(alert)
                
                time.sleep(1)  # Check queue every second
                
            except Exception as e:
                self.logger.error("Alert processing error: %s", e)
    
    def create_alert(self, alert_id, severity, title, message, metadata=None):
        """Create new alert"""
        alert = {
            'alert_id': alert_id,
            'severity': severity.lower(),
            'title': title,
            'message': message,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat(),
            'created_at': datetime.now()
        }
        
        # Log to database
        self._log_alert(alert)
        
        # Determine channels and processing
        rule = self.config['alert_rules'].get(severity.lower(), {})
        channels = rule.get('channels', [])
        immediate = rule.get('immediate', True)
        
        alert['channels'] = channels
        
        if immediate:
            # Send immediately
            with self.queue_lock:
                self.alert_queue.append(alert)
        else:
            # Batch processing (simplified for now)
            with self.queue_lock:
                self.alert_queue.append(alert)
        
        self.logger.info("Alert created: %s (%s)", alert_id, severity)
    
    def _log_alert(self, alert):
        """Log alert to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alert_history 
                (alert_id, severity, title, message, channels, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert['alert_id'],
                alert['severity'],
                alert['title'],
                alert['message'],
                ','.join(alert.get('channels', [])),
                'pending'
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error("Failed to log alert: %s", e)
    
    def _send_alert(self, alert):
        """Send alert through configured channels"""
        channels = alert.get('channels', [])
        sent_channels = []
        errors = []
        
        for channel in channels:
            try:
                if channel == 'email' and self.config['email']['enabled']:
                    self._send_email_alert(alert)
                    sent_channels.append('email')
                
                elif channel == 'slack' and self.config['slack']['enabled']:
                    self._send_slack_alert(alert)
                    sent_channels.append('slack')
                
                elif channel == 'teams' and self.config['teams']['enabled']:
                    self._send_teams_alert(alert)
                    sent_channels.append('teams')
                
                elif channel == 'discord' and self.config['discord']['enabled']:
                    self._send_discord_alert(alert)
                    sent_channels.append('discord')
                
            except Exception as e:
                error_msg = f"{channel}: {str(e)}"
                errors.append(error_msg)
                self.logger.error("Failed to send %s alert: %s", channel, e)
        
        # Update database
        self._update_alert_status(
            alert['alert_id'],
            'sent' if sent_channels else 'failed',
            sent_channels,
            errors
        )
    
    def _send_email_alert(self, alert):
        """Send email alert"""
        config = self.config['email']
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 {alert['title']}"
        msg['From'] = config['from_address']
        msg['To'] = ', '.join(config['to_addresses'])
        
        # Create HTML content
        html_content = f"""
        <html>
        <body>
            <h2 style="color: #e74c3c;">Security Alert</h2>
            <p><strong>Severity:</strong> {alert['severity'].upper()}</p>
            <p><strong>Title:</strong> {alert['title']}</p>
            <p><strong>Message:</strong> {alert['message']}</p>
            <p><strong>Timestamp:</strong> {alert['timestamp']}</p>
            
            <p style="color: #7f8c8d; font-size: 12px;">
                This alert was generated by Security Bot Enterprise
            </p>
        </body>
        </html>
        """
        
        part = MIMEText(html_content, 'html')
        msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['username'], config['password'])
        
        for to_address in config['to_addresses']:
            server.send_message(msg, to_addrs=[to_address])
        
        server.quit()
    
    def _send_slack_alert(self, alert):
        """Send Slack alert"""
        config = self.config['slack']
        
        # Severity colors
        colors = {
            'critical': '#e74c3c',
            'high': '#f39c12',
            'medium': '#f1c40f',
            'low': '#27ae60'
        }
        
        payload = {
            "channel": config['channel'],
            "username": "Security Bot",
            "icon_emoji": ":shield:",
            "attachments": [{
                "color": colors.get(alert['severity'], '#3498db'),
                "title": f"🚨 {alert['title']}",
                "fields": [
                    {
                        "title": "Severity",
                        "value": alert['severity'].upper(),
                        "short": True
                    },
                    {
                        "title": "Timestamp",
                        "value": alert['timestamp'],
                        "short": True
                    },
                    {
                        "title": "Message",
                        "value": alert['message'],
                        "short": False
                    }
                ],
                "footer": "Security Bot Enterprise",
                "ts": int(alert['created_at'].timestamp())
            }]
        }
        
        response = requests.post(config['webhook_url'], json=payload, timeout=10)
        response.raise_for_status()
    
    def _send_teams_alert(self, alert):
        """Send Microsoft Teams alert"""
        config = self.config['teams']
        
        # Severity colors
        colors = {
            'critical': 'attention',
            'high': 'warning',
            'medium': 'good',
            'low': 'accent'
        }
        
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": colors.get(alert['severity'], 'accent'),
            "summary": f"Security Alert: {alert['title']}",
            "sections": [{
                "activityTitle": "🛡️ Security Bot Enterprise",
                "activitySubtitle": f"**{alert['severity'].upper()}** Alert",
                "facts": [
                    {
                        "name": "Title",
                        "value": alert['title']
                    },
                    {
                        "name": "Severity",
                        "value": alert['severity'].upper()
                    },
                    {
                        "name": "Timestamp",
                        "value": alert['timestamp']
                    },
                    {
                        "name": "Message",
                        "value": alert['message']
                    }
                ],
                "markdown": True
            }]
        }
        
        response = requests.post(config['webhook_url'], json=payload, timeout=10)
        response.raise_for_status()
    
    def _send_discord_alert(self, alert):
        """Send Discord alert"""
        config = self.config['discord']
        
        # Severity colors (Discord color codes)
        colors = {
            'critical': 15158332,  # Red
            'high': 15105570,      # Orange
            'medium': 16776960,    # Yellow
            'low': 5763719         # Green
        }
        
        payload = {
            "embeds": [{
                "title": f"🚨 {alert['title']}",
                "description": alert['message'],
                "color": colors.get(alert['severity'], 3447003),
                "fields": [
                    {
                        "name": "Severity",
                        "value": alert['severity'].upper(),
                        "inline": True
                    },
                    {
                        "name": "Timestamp",
                        "value": alert['timestamp'],
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Security Bot Enterprise"
                },
                "timestamp": alert['timestamp']
            }]
        }
        
        response = requests.post(config['webhook_url'], json=payload, timeout=10)
        response.raise_for_status()
    
    def _update_alert_status(self, alert_id, status, channels=None, errors=None):
        """Update alert status in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            error_message = '; '.join(errors) if errors else None
            
            cursor.execute("""
                UPDATE alert_history 
                SET status = ?, sent_at = CURRENT_TIMESTAMP, error_message = ?
                WHERE alert_id = ?
            """, (status, error_message, alert_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error("Failed to update alert status: %s", e)
    
    def test_channels(self):
        """Test all configured notification channels"""
        test_alert = {
            'alert_id': f'test_{int(time.time())}',
            'severity': 'low',
            'title': 'Test Alert',
            'message': 'This is a test alert from Security Bot Enterprise',
            'timestamp': datetime.now().isoformat(),
            'created_at': datetime.now(),
            'channels': ['email', 'slack', 'teams', 'discord']
        }
        
        self._send_alert(test_alert)
        self.logger.info("Test alerts sent")
    
    def get_alert_history(self, limit=100):
        """Get alert history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT alert_id, severity, title, message, channels, status, 
                       created_at, sent_at, error_message
                FROM alert_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            alerts = cursor.fetchall()
            conn.close()
            
            return alerts
            
        except Exception as e:
            self.logger.error("Failed to get alert history: %s", e)
            return []


if __name__ == '__main__':
    # Test alerting system
    alerting = AlertingSystem()
    alerting.start_processor()
    
    # Create test alert
    alerting.create_alert(
        alert_id="test_001",
        severity="high",
        title="Suspicious Network Activity",
        message="Multiple failed login attempts detected from IP 192.168.1.100",
        metadata={"source_ip": "192.168.1.100", "attempts": 5}
    )
    
    time.sleep(2)
    alerting.stop_processor()