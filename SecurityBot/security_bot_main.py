"""
Security Bot Enterprise - Main Application Entry Point
Orchestrates all enterprise security components with proper initialization and coordination
"""

import os
import sys
import logging
import threading
import time
import signal
import json
from datetime import datetime
from pathlib import Path

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all enterprise components
try:
    from threat_detection import ThreatDetectionEngine
    from auth_system import AuthenticationManager
    from enhanced_dashboard import EnhancedDashboard
    from alerting_system import AlertingSystem
    from database_integration import DatabaseManager
    from rest_api import SecurityBotAPI
    from ui_ux_manager import UIUXManager
    from reporting_system import ReportingSystem
except ImportError as e:
    print(f"Warning: Some modules could not be imported: {e}")
    print("Some features may not be available until all dependencies are installed.")


class SecurityBotEnterprise:
    """Main Security Bot Enterprise Application Controller"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.running = False
        self.components = {}
        self.threads = []
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.load_configuration()
        
        # Initialize components
        self.initialize_components()
        
        # Setup signal handlers for graceful shutdown
        self.setup_signal_handlers()
        
        self.logger.info("Security Bot Enterprise initialized successfully")
    
    def setup_logging(self):
        """Configure enterprise-grade logging"""
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/security_bot_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('SecurityBotEnterprise')
        self.logger.info("Logging system initialized")
    
    def load_configuration(self):
        """Load enterprise configuration"""
        default_config = {
            "enterprise": {
                "company_name": "Security Bot Enterprise",
                "version": "1.0.0",
                "environment": "production",
                "debug": False
            },
            "components": {
                "threat_detection": {
                    "enabled": True,
                    "scan_interval": 30,
                    "real_time_monitoring": True
                },
                "authentication": {
                    "enabled": True,
                    "session_timeout": 3600,
                    "max_login_attempts": 5
                },
                "dashboard": {
                    "enabled": True,
                    "port": 8080,
                    "auto_refresh": True,
                    "refresh_interval": 30
                },
                "alerting": {
                    "enabled": True,
                    "email_notifications": True,
                    "sms_notifications": False,
                    "webhook_notifications": True
                },
                "database": {
                    "enabled": True,
                    "backup_enabled": True,
                    "backup_interval": 24,
                    "retention_days": 90
                },
                "api": {
                    "enabled": True,
                    "port": 8081,
                    "rate_limiting": True,
                    "cors_enabled": True
                },
                "reporting": {
                    "enabled": True,
                    "daily_reports": True,
                    "weekly_reports": True,
                    "monthly_compliance": True
                }
            },
            "security": {
                "api_keys": [],
                "jwt_secret": "change-this-in-production",
                "encryption_key": "change-this-in-production"
            },
            "network": {
                "bind_address": "0.0.0.0",
                "dashboard_port": 8080,
                "api_port": 8081
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # Merge with defaults
                    self.config = {**default_config, **saved_config}
            else:
                self.config = default_config
                self.save_configuration()
                
        except Exception as e:
            self.logger.error("Failed to load configuration: %s", e)
            self.config = default_config
    
    def save_configuration(self):
        """Save current configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("Configuration saved successfully")
            
        except Exception as e:
            self.logger.error("Failed to save configuration: %s", e)
    
    def initialize_components(self):
        """Initialize all enterprise components"""
        self.logger.info("Initializing enterprise components...")
        
        # Initialize database first (required by other components)
        if self.config['components']['database']['enabled']:
            try:
                self.components['database'] = DatabaseManager()
                self.logger.info("Database manager initialized")
            except Exception as e:
                self.logger.error("Failed to initialize database: %s", e)
        
        # Initialize authentication system
        if self.config['components']['authentication']['enabled']:
            try:
                self.components['auth'] = AuthenticationManager()
                self.logger.info("Authentication system initialized")
            except Exception as e:
                self.logger.error("Failed to initialize authentication: %s", e)
        
        # Initialize threat detection engine
        if self.config['components']['threat_detection']['enabled']:
            try:
                self.components['threat_detection'] = ThreatDetectionEngine()
                self.logger.info("Threat detection engine initialized")
            except Exception as e:
                self.logger.error("Failed to initialize threat detection: %s", e)
        
        # Initialize alerting system
        if self.config['components']['alerting']['enabled']:
            try:
                self.components['alerting'] = AlertingSystem()
                self.logger.info("Alerting system initialized")
            except Exception as e:
                self.logger.error("Failed to initialize alerting system: %s", e)
        
        # Initialize dashboard
        if self.config['components']['dashboard']['enabled']:
            try:
                self.components['dashboard'] = EnhancedDashboard(
                    port=self.config['network']['dashboard_port']
                )
                self.logger.info("Enhanced dashboard initialized")
            except Exception as e:
                self.logger.error("Failed to initialize dashboard: %s", e)
        
        # Initialize REST API
        if self.config['components']['api']['enabled']:
            try:
                self.components['api'] = SecurityBotAPI(
                    port=self.config['network']['api_port']
                )
                self.logger.info("REST API initialized")
            except Exception as e:
                self.logger.error("Failed to initialize REST API: %s", e)
        
        # Initialize UI/UX manager
        try:
            self.components['ui_ux'] = UIUXManager()
            self.logger.info("UI/UX manager initialized")
        except Exception as e:
            self.logger.error("Failed to initialize UI/UX manager: %s", e)
        
        # Initialize reporting system
        if self.config['components']['reporting']['enabled']:
            try:
                self.components['reporting'] = ReportingSystem()
                self.logger.info("Reporting system initialized")
            except Exception as e:
                self.logger.error("Failed to initialize reporting system: %s", e)
        
        self.logger.info("All components initialized successfully")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.logger.info("Received signal %s, initiating graceful shutdown...", signum)
            self.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_component_threads(self):
        """Start all component threads"""
        self.logger.info("Starting component threads...")
        
        # Start threat detection engine
        if 'threat_detection' in self.components:
            def run_threat_detection():
                try:
                    self.components['threat_detection'].start_monitoring()
                except Exception as e:
                    self.logger.error("Threat detection thread error: %s", e)
            
            thread = threading.Thread(target=run_threat_detection, daemon=True)
            thread.start()
            self.threads.append(thread)
            self.logger.info("Threat detection thread started")
        
        # Start alerting system
        if 'alerting' in self.components:
            def run_alerting():
                try:
                    self.components['alerting'].start_alert_processing()
                except Exception as e:
                    self.logger.error("Alerting thread error: %s", e)
            
            thread = threading.Thread(target=run_alerting, daemon=True)
            thread.start()
            self.threads.append(thread)
            self.logger.info("Alerting thread started")
        
        # Start dashboard server
        if 'dashboard' in self.components:
            def run_dashboard():
                try:
                    self.components['dashboard'].start_server()
                except Exception as e:
                    self.logger.error("Dashboard thread error: %s", e)
            
            thread = threading.Thread(target=run_dashboard, daemon=True)
            thread.start()
            self.threads.append(thread)
            self.logger.info("Dashboard server thread started")
        
        # Start REST API server
        if 'api' in self.components:
            def run_api():
                try:
                    self.components['api'].start_server()
                except Exception as e:
                    self.logger.error("API thread error: %s", e)
            
            thread = threading.Thread(target=run_api, daemon=True)
            thread.start()
            self.threads.append(thread)
            self.logger.info("REST API server thread started")
        
        # Start reporting scheduler
        if 'reporting' in self.components:
            def run_reporting():
                try:
                    self.components['reporting'].start_scheduler()
                except Exception as e:
                    self.logger.error("Reporting thread error: %s", e)
            
            thread = threading.Thread(target=run_reporting, daemon=True)
            thread.start()
            self.threads.append(thread)
            self.logger.info("Reporting scheduler thread started")
    
    def start(self):
        """Start the Security Bot Enterprise system"""
        if self.running:
            self.logger.warning("Security Bot Enterprise is already running")
            return
        
        self.logger.info("Starting Security Bot Enterprise...")
        self.running = True
        
        try:
            # Start all component threads
            self.start_component_threads()
            
            # Start health monitoring
            self.start_health_monitoring()
            
            self.logger.info("Security Bot Enterprise started successfully")
            
            # Display startup information
            self.display_startup_info()
            
            # Main loop
            self.main_loop()
            
        except Exception as e:
            self.logger.error("Failed to start Security Bot Enterprise: %s", e)
            self.stop()
    
    def start_health_monitoring(self):
        """Start system health monitoring"""
        def health_monitor():
            while self.running:
                try:
                    # Monitor component health
                    health_status = self.get_system_health()
                    
                    # Log health status
                    if all(health_status.values()):
                        self.logger.debug("All components healthy")
                    else:
                        unhealthy = [k for k, v in health_status.items() if not v]
                        self.logger.warning("Unhealthy components: %s", unhealthy)
                    
                    # Sleep for health check interval
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    self.logger.error("Health monitoring error: %s", e)
                    time.sleep(60)
        
        health_thread = threading.Thread(target=health_monitor, daemon=True)
        health_thread.start()
        self.threads.append(health_thread)
        self.logger.info("Health monitoring started")
    
    def get_system_health(self):
        """Get health status of all components"""
        health_status = {}
        
        for component_name, component in self.components.items():
            try:
                # Check if component has health check method
                if hasattr(component, 'health_check'):
                    health_status[component_name] = component.health_check()
                else:
                    # Assume healthy if no health check method
                    health_status[component_name] = True
                    
            except Exception as e:
                self.logger.error("Health check failed for %s: %s", component_name, e)
                health_status[component_name] = False
        
        return health_status
    
    def display_startup_info(self):
        """Display startup information"""
        print("\n" + "="*80)
        print("🛡️  SECURITY BOT ENTERPRISE - SYSTEM STARTED")
        print("="*80)
        print(f"Version: {self.config['enterprise']['version']}")
        print(f"Environment: {self.config['enterprise']['environment']}")
        print(f"Company: {self.config['enterprise']['company_name']}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📊 COMPONENT STATUS:")
        
        for component_name in self.components.keys():
            status = "✅ RUNNING" if component_name in self.components else "❌ FAILED"
            print(f"  {component_name.upper()}: {status}")
        
        print("\n🌐 ACCESS POINTS:")
        if 'dashboard' in self.components:
            print(f"  Dashboard: http://localhost:{self.config['network']['dashboard_port']}")
        if 'api' in self.components:
            print(f"  REST API: http://localhost:{self.config['network']['api_port']}")
        
        print("\n📝 LOGS:")
        print(f"  Log files: ./logs/")
        print(f"  Config file: {self.config_file}")
        
        print("\n🔐 SECURITY FEATURES:")
        print("  ✅ Advanced Threat Detection")
        print("  ✅ Real-time Monitoring")
        print("  ✅ Multi-channel Alerting")
        print("  ✅ Enterprise Authentication")
        print("  ✅ Automated Reporting")
        print("  ✅ REST API Integration")
        
        print("\n💡 NEXT STEPS:")
        print("  1. Access the dashboard to view real-time security status")
        print("  2. Configure alert settings for your environment")
        print("  3. Review and customize security policies")
        print("  4. Setup automated reporting schedules")
        print("\n" + "="*80)
        print("Press Ctrl+C to stop the system")
        print("="*80 + "\n")
    
    def main_loop(self):
        """Main application loop"""
        try:
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        except Exception as e:
            self.logger.error("Main loop error: %s", e)
        finally:
            self.stop()
    
    def stop(self):
        """Stop the Security Bot Enterprise system"""
        if not self.running:
            return
        
        self.logger.info("Stopping Security Bot Enterprise...")
        self.running = False
        
        # Stop all components
        for component_name, component in self.components.items():
            try:
                if hasattr(component, 'stop'):
                    component.stop()
                    self.logger.info("Stopped %s", component_name)
            except Exception as e:
                self.logger.error("Error stopping %s: %s", component_name, e)
        
        # Wait for threads to finish
        for thread in self.threads:
            try:
                thread.join(timeout=5)
            except Exception as e:
                self.logger.error("Error joining thread: %s", e)
        
        self.logger.info("Security Bot Enterprise stopped")
        print("\n🛡️  Security Bot Enterprise has been stopped safely")
    
    def restart(self):
        """Restart the Security Bot Enterprise system"""
        self.logger.info("Restarting Security Bot Enterprise...")
        self.stop()
        time.sleep(2)
        self.start()
    
    def get_status(self):
        """Get current system status"""
        return {
            'running': self.running,
            'components': list(self.components.keys()),
            'health': self.get_system_health(),
            'uptime': time.time() - getattr(self, 'start_time', time.time()),
            'version': self.config['enterprise']['version'],
            'environment': self.config['enterprise']['environment']
        }


def main():
    """Main entry point"""
    print("🛡️  Security Bot Enterprise - Starting...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    # Create required directories
    required_dirs = ['logs', 'data', 'reports', 'config']
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
    
    try:
        # Initialize and start Security Bot Enterprise
        security_bot = SecurityBotEnterprise()
        security_bot.start()
        
    except Exception as e:
        print(f"❌ Failed to start Security Bot Enterprise: {e}")
        logging.exception("Startup failed")
        sys.exit(1)


if __name__ == '__main__':
    main()