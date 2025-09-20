"""
Security Bot Enterprise - Deployment Script
Comprehensive deployment automation for Windows enterprise environments
"""

import os
import sys
import subprocess
import json
import shutil
import winreg
from pathlib import Path
import zipfile
import requests
from datetime import datetime
import logging


class SecurityBotDeployer:
    """Enterprise deployment manager for Security Bot"""
    
    def __init__(self):
        self.deployment_dir = Path(__file__).parent
        self.install_dir = Path("C:/Program Files/SecurityBot Enterprise")
        self.service_name = "SecurityBotEnterprise"
        self.setup_logging()
        
    def setup_logging(self):
        """Setup deployment logging"""
        log_dir = self.deployment_dir / "deployment_logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SecurityBotDeployer')
    
    def check_prerequisites(self):
        """Check system prerequisites for deployment"""
        self.logger.info("Checking system prerequisites...")
        
        prerequisites = {
            'python_version': False,
            'admin_rights': False,
            'required_modules': False,
            'system_compatibility': False
        }
        
        # Check Python version
        if sys.version_info >= (3, 7):
            prerequisites['python_version'] = True
            self.logger.info("✅ Python version: %s", sys.version.split()[0])
        else:
            self.logger.error("❌ Python 3.7+ required, found: %s", sys.version.split()[0])
        
        # Check admin rights
        try:
            import ctypes
            if ctypes.windll.shell32.IsUserAnAdmin():
                prerequisites['admin_rights'] = True
                self.logger.info("✅ Administrator rights: Available")
            else:
                self.logger.error("❌ Administrator rights: Required for installation")
        except Exception as e:
            self.logger.error("❌ Cannot check admin rights: %s", e)
        
        # Check system compatibility
        if sys.platform == 'win32':
            prerequisites['system_compatibility'] = True
            self.logger.info("✅ System compatibility: Windows detected")
        else:
            self.logger.error("❌ System compatibility: Windows required")
        
        # Check/install required modules
        required_modules = [
            'flask', 'flask-cors', 'flask-limiter', 'psutil', 'sqlite3', 
            'bcrypt', 'PyJWT', 'schedule', 'requests', 'twilio'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                if module == 'sqlite3':
                    import sqlite3
                elif module == 'PyJWT':
                    import jwt
                else:
                    __import__(module.replace('-', '_'))
                self.logger.debug("✅ Module available: %s", module)
            except ImportError:
                missing_modules.append(module)
                self.logger.warning("⚠️  Module missing: %s", module)
        
        if not missing_modules:
            prerequisites['required_modules'] = True
            self.logger.info("✅ All required modules available")
        else:
            self.logger.info("📦 Will install missing modules: %s", missing_modules)
            prerequisites['required_modules'] = self.install_dependencies(missing_modules)
        
        return prerequisites
    
    def install_dependencies(self, modules):
        """Install required Python dependencies"""
        self.logger.info("Installing required dependencies...")
        
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            
            # Install required modules
            for module in modules:
                self.logger.info("Installing %s...", module)
                result = subprocess.run([sys.executable, '-m', 'pip', 'install', module], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info("✅ Successfully installed %s", module)
                else:
                    self.logger.error("❌ Failed to install %s: %s", module, result.stderr)
                    return False
            
            # Install optional dependencies for enhanced features
            optional_modules = ['reportlab', 'Pillow']
            for module in optional_modules:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', module], 
                                 capture_output=True, check=True)
                    self.logger.info("✅ Installed optional module: %s", module)
                except subprocess.CalledProcessError:
                    self.logger.warning("⚠️  Optional module %s not installed", module)
            
            return True
            
        except Exception as e:
            self.logger.error("❌ Failed to install dependencies: %s", e)
            return False
    
    def create_directory_structure(self):
        """Create required directory structure"""
        self.logger.info("Creating directory structure...")
        
        directories = [
            self.install_dir,
            self.install_dir / "logs",
            self.install_dir / "data",
            self.install_dir / "reports",
            self.install_dir / "config",
            self.install_dir / "static",
            self.install_dir / "templates",
            self.install_dir / "backups"
        ]
        
        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.debug("Created directory: %s", directory)
            
            self.logger.info("✅ Directory structure created successfully")
            return True
            
        except Exception as e:
            self.logger.error("❌ Failed to create directory structure: %s", e)
            return False
    
    def deploy_application_files(self):
        """Deploy application files to installation directory"""
        self.logger.info("Deploying application files...")
        
        # List of core application files
        core_files = [
            'security_bot_main.py',
            'threat_detection.py',
            'auth_system.py',
            'enhanced_dashboard.py',
            'alerting_system.py',
            'database_integration.py',
            'rest_api.py',
            'ui_ux_manager.py',
            'reporting_system.py'
        ]
        
        try:
            # Copy core application files
            for filename in core_files:
                source = self.deployment_dir / filename
                destination = self.install_dir / filename
                
                if source.exists():
                    shutil.copy2(source, destination)
                    self.logger.debug("Copied: %s", filename)
                else:
                    self.logger.warning("⚠️  File not found: %s", filename)
            
            # Create default configuration
            self.create_default_configuration()
            
            # Create startup scripts
            self.create_startup_scripts()
            
            self.logger.info("✅ Application files deployed successfully")
            return True
            
        except Exception as e:
            self.logger.error("❌ Failed to deploy application files: %s", e)
            return False
    
    def create_default_configuration(self):
        """Create default configuration files"""
        self.logger.info("Creating default configuration...")
        
        # Main configuration
        config = {
            "enterprise": {
                "company_name": "Your Company",
                "version": "1.0.0",
                "environment": "production",
                "debug": False
            },
            "components": {
                "threat_detection": {"enabled": True, "scan_interval": 30},
                "authentication": {"enabled": True, "session_timeout": 3600},
                "dashboard": {"enabled": True, "port": 8080},
                "alerting": {"enabled": True, "email_notifications": True},
                "database": {"enabled": True, "backup_enabled": True},
                "api": {"enabled": True, "port": 8081},
                "reporting": {"enabled": True, "daily_reports": True}
            },
            "security": {
                "jwt_secret": "change-this-in-production-" + datetime.now().strftime('%Y%m%d%H%M%S'),
                "encryption_key": "change-this-in-production-" + datetime.now().strftime('%Y%m%d%H%M%S')
            },
            "network": {
                "bind_address": "127.0.0.1",
                "dashboard_port": 8080,
                "api_port": 8081
            }
        }
        
        config_file = self.install_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        # Alerting configuration
        alerting_config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": "security@yourcompany.com"
            },
            "notifications": {
                "critical_threats": True,
                "system_alerts": True,
                "daily_summaries": True
            }
        }
        
        alerting_file = self.install_dir / "alerting_config.json"
        with open(alerting_file, 'w', encoding='utf-8') as f:
            json.dump(alerting_config, f, indent=2)
        
        # Reporting configuration
        reporting_config = {
            "schedules": {
                "daily_summary": {"enabled": True, "time": "08:00", "recipients": []},
                "weekly_report": {"enabled": True, "day": "Monday", "time": "09:00", "recipients": []},
                "monthly_compliance": {"enabled": True, "day": 1, "time": "10:00", "recipients": []}
            },
            "report_settings": {
                "company_name": "Your Company",
                "contact_info": "security@yourcompany.com"
            }
        }
        
        reporting_file = self.install_dir / "reporting_config.json"
        with open(reporting_file, 'w', encoding='utf-8') as f:
            json.dump(reporting_config, f, indent=2)
        
        self.logger.info("✅ Default configuration created")
    
    def create_startup_scripts(self):
        """Create startup and service scripts"""
        self.logger.info("Creating startup scripts...")
        
        # Windows batch script for manual startup
        batch_script = f"""@echo off
title Security Bot Enterprise
echo Starting Security Bot Enterprise...
cd /d "{self.install_dir}"
python security_bot_main.py
pause
"""
        
        batch_file = self.install_dir / "start_security_bot.bat"
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_script)
        
        # PowerShell script for advanced startup
        ps_script = f"""# Security Bot Enterprise Startup Script
Set-Location "{self.install_dir}"
Write-Host "Starting Security Bot Enterprise..." -ForegroundColor Green

try {{
    python security_bot_main.py
}} catch {{
    Write-Host "Error starting Security Bot: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}}
"""
        
        ps_file = self.install_dir / "start_security_bot.ps1"
        with open(ps_file, 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        # Create uninstaller
        uninstall_script = f"""@echo off
title Security Bot Enterprise Uninstaller
echo Uninstalling Security Bot Enterprise...

rem Stop service if running
sc stop "{self.service_name}" 2>nul
sc delete "{self.service_name}" 2>nul

rem Remove startup registry entry
reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" /v "SecurityBotEnterprise" /f 2>nul

rem Remove installation directory
echo Removing installation files...
timeout /t 3 /nobreak
rmdir /s /q "{self.install_dir}" 2>nul

echo Security Bot Enterprise has been uninstalled.
pause
"""
        
        uninstall_file = self.install_dir / "uninstall.bat"
        with open(uninstall_file, 'w', encoding='utf-8') as f:
            f.write(uninstall_script)
        
        self.logger.info("✅ Startup scripts created")
    
    def configure_windows_startup(self):
        """Configure Windows startup integration"""
        self.logger.info("Configuring Windows startup...")
        
        try:
            # Add to Windows startup registry
            startup_command = f'python "{self.install_dir / "security_bot_main.py"}"'
            
            # Open registry key for startup programs
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            
            # Set the value
            winreg.SetValueEx(key, "SecurityBotEnterprise", 0, winreg.REG_SZ, startup_command)
            winreg.CloseKey(key)
            
            self.logger.info("✅ Windows startup configured")
            return True
            
        except Exception as e:
            self.logger.error("❌ Failed to configure Windows startup: %s", e)
            return False
    
    def create_desktop_shortcuts(self):
        """Create desktop shortcuts"""
        self.logger.info("Creating desktop shortcuts...")
        
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            
            # Main application shortcut
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(os.path.join(desktop, 'Security Bot Enterprise.lnk'))
            shortcut.Targetpath = str(self.install_dir / "start_security_bot.bat")
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = str(self.install_dir / "start_security_bot.bat")
            shortcut.save()
            
            # Dashboard shortcut
            dashboard_shortcut = shell.CreateShortCut(os.path.join(desktop, 'Security Bot Dashboard.lnk'))
            dashboard_shortcut.Targetpath = "http://localhost:8080"
            dashboard_shortcut.save()
            
            self.logger.info("✅ Desktop shortcuts created")
            return True
            
        except ImportError:
            self.logger.warning("⚠️  winshell not available, skipping desktop shortcuts")
            return True
        except Exception as e:
            self.logger.error("❌ Failed to create desktop shortcuts: %s", e)
            return False
    
    def configure_firewall(self):
        """Configure Windows Firewall rules"""
        self.logger.info("Configuring Windows Firewall...")
        
        try:
            # Add firewall rules for dashboard and API ports
            commands = [
                f'netsh advfirewall firewall add rule name="Security Bot Dashboard" dir=in action=allow protocol=TCP localport=8080',
                f'netsh advfirewall firewall add rule name="Security Bot API" dir=in action=allow protocol=TCP localport=8081'
            ]
            
            for command in commands:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.debug("Firewall rule added successfully")
                else:
                    self.logger.warning("Failed to add firewall rule: %s", result.stderr)
            
            self.logger.info("✅ Firewall configuration completed")
            return True
            
        except Exception as e:
            self.logger.error("❌ Failed to configure firewall: %s", e)
            return False
    
    def run_post_deployment_tests(self):
        """Run post-deployment verification tests"""
        self.logger.info("Running post-deployment tests...")
        
        tests_passed = 0
        total_tests = 5
        
        # Test 1: Check file existence
        required_files = ['security_bot_main.py', 'config.json']
        files_exist = all((self.install_dir / f).exists() for f in required_files)
        if files_exist:
            tests_passed += 1
            self.logger.info("✅ Test 1: Required files exist")
        else:
            self.logger.error("❌ Test 1: Required files missing")
        
        # Test 2: Check directory structure
        required_dirs = ['logs', 'data', 'reports', 'config']
        dirs_exist = all((self.install_dir / d).exists() for d in required_dirs)
        if dirs_exist:
            tests_passed += 1
            self.logger.info("✅ Test 2: Directory structure correct")
        else:
            self.logger.error("❌ Test 2: Directory structure incomplete")
        
        # Test 3: Check configuration validity
        try:
            with open(self.install_dir / "config.json", 'r') as f:
                config = json.load(f)
            if config.get('enterprise', {}).get('version'):
                tests_passed += 1
                self.logger.info("✅ Test 3: Configuration valid")
            else:
                self.logger.error("❌ Test 3: Invalid configuration")
        except Exception:
            self.logger.error("❌ Test 3: Configuration error")
        
        # Test 4: Check Python module imports
        try:
            import sys
            sys.path.insert(0, str(self.install_dir))
            import security_bot_main
            tests_passed += 1
            self.logger.info("✅ Test 4: Python imports successful")
        except Exception as e:
            self.logger.error("❌ Test 4: Import error: %s", e)
        
        # Test 5: Check startup script
        startup_script = self.install_dir / "start_security_bot.bat"
        if startup_script.exists():
            tests_passed += 1
            self.logger.info("✅ Test 5: Startup script exists")
        else:
            self.logger.error("❌ Test 5: Startup script missing")
        
        success_rate = (tests_passed / total_tests) * 100
        self.logger.info("Post-deployment tests: %d/%d passed (%.1f%%)", tests_passed, total_tests, success_rate)
        
        return tests_passed == total_tests
    
    def deploy(self):
        """Execute complete deployment process"""
        self.logger.info("Starting Security Bot Enterprise deployment...")
        
        deployment_steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Creating directory structure", self.create_directory_structure),
            ("Deploying application files", self.deploy_application_files),
            ("Configuring Windows startup", self.configure_windows_startup),
            ("Creating desktop shortcuts", self.create_desktop_shortcuts),
            ("Configuring firewall", self.configure_firewall),
            ("Running post-deployment tests", self.run_post_deployment_tests)
        ]
        
        success_count = 0
        total_steps = len(deployment_steps)
        
        for step_name, step_function in deployment_steps:
            self.logger.info("Step: %s", step_name)
            try:
                if callable(step_function):
                    if step_name == "Checking prerequisites":
                        result = step_function()
                        if all(result.values()):
                            success_count += 1
                        else:
                            self.logger.error("Prerequisites not met: %s", 
                                            [k for k, v in result.items() if not v])
                    else:
                        if step_function():
                            success_count += 1
                else:
                    success_count += 1
                    
            except Exception as e:
                self.logger.error("Step failed: %s - %s", step_name, e)
        
        # Deployment summary
        self.logger.info("="*60)
        if success_count == total_steps:
            self.logger.info("🎉 DEPLOYMENT SUCCESSFUL!")
            self.logger.info("Security Bot Enterprise has been deployed successfully.")
            self.logger.info("Installation directory: %s", self.install_dir)
            self.logger.info("To start the system:")
            self.logger.info("  1. Run: %s", self.install_dir / "start_security_bot.bat")
            self.logger.info("  2. Or access via desktop shortcut")
            self.logger.info("  3. Dashboard will be available at: http://localhost:8080")
            self.logger.info("  4. REST API will be available at: http://localhost:8081")
        else:
            self.logger.error("⚠️  DEPLOYMENT PARTIALLY SUCCESSFUL")
            self.logger.error("Completed: %d/%d steps", success_count, total_steps)
            self.logger.error("Please check the logs and resolve any issues.")
        
        self.logger.info("="*60)
        
        return success_count == total_steps


def main():
    """Main deployment entry point"""
    print("🛡️  Security Bot Enterprise - Deployment Utility")
    print("="*60)
    
    try:
        deployer = SecurityBotDeployer()
        success = deployer.deploy()
        
        if success:
            print("\n✅ Deployment completed successfully!")
            print("You can now start Security Bot Enterprise.")
        else:
            print("\n⚠️  Deployment completed with warnings.")
            print("Please check the deployment logs for details.")
            
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        logging.exception("Deployment error")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())