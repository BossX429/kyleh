"""
Security Bot Enterprise - Deployment Verification
Test script to verify all components are working correctly
"""

import sys
import logging
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

def setup_logging():
    """Setup verification logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('deployment_verification.log')
        ]
    )
    return logging.getLogger('DeploymentVerification')


def test_imports():
    """Test all module imports"""
    logger = logging.getLogger('DeploymentVerification')
    logger.info("Testing module imports...")
    
    modules_to_test = [
        'threat_detection',
        'auth_system', 
        'enhanced_dashboard',
        'alerting_system',
        'database_integration',
        'rest_api',
        'ui_ux_manager',
        'reporting_system'
    ]
    
    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            logger.info("✓ %s imported successfully", module_name)
            success_count += 1
        except Exception as e:
            logger.error("✗ Failed to import %s: %s", module_name, e)
    
    logger.info("Import test results: %d/%d modules imported successfully", 
                success_count, len(modules_to_test))
    return success_count == len(modules_to_test)


def test_database_initialization():
    """Test database initialization"""
    logger = logging.getLogger('DeploymentVerification')
    logger.info("Testing database initialization...")
    
    try:
        from database_integration import DatabaseIntegration
        
        db = DatabaseIntegration("test_security_bot.db")
        
        # Test basic database operations
        test_threat = {
            'threat_id': 'test_verification_001',
            'threat_type': 'test_threat',
            'severity': 'low',
            'source': 'verification_test',
            'target': 'test_system',
            'description': 'Test threat for deployment verification',
            'metadata': {'test': True},
            'risk_score': 10
        }
        
        db.log_threat(test_threat)
        
        # Test statistics
        stats = db.get_threat_statistics(1)
        
        # Clean up test database
        import os
        if os.path.exists("test_security_bot.db"):
            os.remove("test_security_bot.db")
        
        logger.info("✓ Database initialization successful")
        return True
        
    except Exception as e:
        logger.error("✗ Database initialization failed: %s", e)
        return False


def test_authentication_system():
    """Test authentication system"""
    logger = logging.getLogger('DeploymentVerification')
    logger.info("Testing authentication system...")
    
    try:
        from auth_system import AuthenticationSystem
        
        auth = AuthenticationSystem("test_auth.db")
        
        # Test login with default admin
        result = auth.login("admin", "SecurityBot2024!")
        
        if result['success']:
            # Test token verification
            token = result['token']
            verify_result = auth.verify_token(token)
            
            if verify_result['success']:
                logger.info("✓ Authentication system working correctly")
                
                # Clean up test database
                import os
                if os.path.exists("test_auth.db"):
                    os.remove("test_auth.db")
                
                return True
        
        logger.error("✗ Authentication test failed")
        return False
        
    except Exception as e:
        logger.error("✗ Authentication system test failed: %s", e)
        return False


def test_threat_detection():
    """Test threat detection engine"""
    logger = logging.getLogger('DeploymentVerification')
    logger.info("Testing threat detection engine...")
    
    try:
        from threat_detection import ThreatDetectionEngine
        from database_integration import DatabaseIntegration
        
        db = DatabaseIntegration("test_threat_detection.db")
        threat_engine = ThreatDetectionEngine(db)
        
        # Test threat detection initialization
        logger.info("✓ Threat detection engine initialized successfully")
        
        # Clean up test database
        import os
        if os.path.exists("test_threat_detection.db"):
            os.remove("test_threat_detection.db")
        
        return True
        
    except Exception as e:
        logger.error("✗ Threat detection test failed: %s", e)
        return False


def test_alerting_system():
    """Test alerting system"""
    logger = logging.getLogger('DeploymentVerification')
    logger.info("Testing alerting system...")
    
    try:
        from alerting_system import AlertingSystem
        
        alerting = AlertingSystem("test_alerting_config.json", "test_alerting.db")
        
        # Test alert creation
        alerting.create_alert(
            alert_id="test_verification_alert",
            severity="low",
            title="Test Alert",
            message="This is a test alert for deployment verification"
        )
        
        logger.info("✓ Alerting system working correctly")
        
        # Clean up test files
        import os
        if os.path.exists("test_alerting.db"):
            os.remove("test_alerting.db")
        if os.path.exists("test_alerting_config.json"):
            os.remove("test_alerting_config.json")
        
        return True
        
    except Exception as e:
        logger.error("✗ Alerting system test failed: %s", e)
        return False


def test_reporting_system():
    """Test reporting system"""
    logger = logging.getLogger('DeploymentVerification')
    logger.info("Testing reporting system...")
    
    try:
        from reporting_system import ReportingSystem
        
        reporting = ReportingSystem("test_reports.db", "test_reports")
        
        # Test report generation
        report = reporting.generate_threat_summary_report(7, 'text')
        
        if report and len(report) > 0:
            logger.info("✓ Reporting system working correctly")
            
            # Clean up test files
            import os
            import shutil
            if os.path.exists("test_reports.db"):
                os.remove("test_reports.db")
            if os.path.exists("test_reports"):
                shutil.rmtree("test_reports")
            
            return True
        else:
            logger.error("✗ Report generation failed")
            return False
        
    except Exception as e:
        logger.error("✗ Reporting system test failed: %s", e)
        return False


def test_ui_ux_manager():
    """Test UI/UX manager"""
    logger = logging.getLogger('DeploymentVerification')
    logger.info("Testing UI/UX manager...")
    
    try:
        from ui_ux_manager import UIUXManager
        
        ui_manager = UIUXManager("test_static", "test_templates")
        
        # Check if static files were created
        static_dir = Path("test_static")
        if static_dir.exists():
            css_file = static_dir / "main.css"
            js_file = static_dir / "main.js"
            
            if css_file.exists() and js_file.exists():
                logger.info("✓ UI/UX manager working correctly")
                
                # Clean up test files
                import shutil
                if static_dir.exists():
                    shutil.rmtree(static_dir)
                
                templates_dir = Path("test_templates")
                if templates_dir.exists():
                    shutil.rmtree(templates_dir)
                
                return True
        
        logger.error("✗ UI/UX manager test failed - static files not created")
        return False
        
    except Exception as e:
        logger.error("✗ UI/UX manager test failed: %s", e)
        return False


def test_enhanced_dashboard():
    """Test enhanced dashboard"""
    logger = logging.getLogger('DeploymentVerification')
    logger.info("Testing enhanced dashboard...")
    
    try:
        from enhanced_dashboard import EnhancedDashboard
        
        dashboard = EnhancedDashboard(port=8081, db_path="test_dashboard.db")
        
        # Test dashboard data retrieval
        data = dashboard.get_dashboard_data()
        
        if data and 'last_updated' in data:
            logger.info("✓ Enhanced dashboard working correctly")
            
            # Clean up test database
            import os
            if os.path.exists("test_dashboard.db"):
                os.remove("test_dashboard.db")
            
            return True
        else:
            logger.error("✗ Dashboard data retrieval failed")
            return False
        
    except Exception as e:
        logger.error("✗ Enhanced dashboard test failed: %s", e)
        return False


def run_comprehensive_verification():
    """Run comprehensive deployment verification"""
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Security Bot Enterprise - Deployment Verification")
    logger.info("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Database Integration", test_database_initialization),
        ("Authentication System", test_authentication_system),
        ("Threat Detection", test_threat_detection),
        ("Alerting System", test_alerting_system),
        ("Reporting System", test_reporting_system),
        ("UI/UX Manager", test_ui_ux_manager),
        ("Enhanced Dashboard", test_enhanced_dashboard)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info("-" * 40)
        logger.info("Running test: %s", test_name)
        
        start_time = time.time()
        try:
            success = test_func()
            end_time = time.time()
            duration = end_time - start_time
            
            results.append({
                'name': test_name,
                'success': success,
                'duration': duration
            })
            
            if success:
                logger.info("✓ %s PASSED (%.2fs)", test_name, duration)
            else:
                logger.error("✗ %s FAILED (%.2fs)", test_name, duration)
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            results.append({
                'name': test_name,
                'success': False,
                'duration': duration,
                'error': str(e)
            })
            
            logger.error("✗ %s FAILED with exception (%.2fs): %s", test_name, duration, e)
    
    # Summary
    logger.info("=" * 60)
    logger.info("DEPLOYMENT VERIFICATION SUMMARY")
    logger.info("=" * 60)
    
    passed_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    total_duration = sum(r['duration'] for r in results)
    
    logger.info("Tests passed: %d/%d", passed_tests, total_tests)
    logger.info("Total duration: %.2f seconds", total_duration)
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED - DEPLOYMENT READY!")
        return True
    else:
        logger.error("❌ SOME TESTS FAILED - DEPLOYMENT NEEDS ATTENTION")
        
        # List failed tests
        failed_tests = [r for r in results if not r['success']]
        logger.error("Failed tests:")
        for test in failed_tests:
            error_msg = test.get('error', 'Test returned False')
            logger.error("  - %s: %s", test['name'], error_msg)
        
        return False


if __name__ == '__main__':
    success = run_comprehensive_verification()
    
    if success:
        print("\n🚀 Security Bot Enterprise is ready for deployment!")
        print("All components have been verified and are working correctly.")
        print("\nNext steps:")
        print("1. Run the main application: python security_bot_main.py")
        print("2. Access the dashboard at: http://localhost:8080")
        print("3. Use the REST API at: http://localhost:5000")
        print("4. Check the deployment script: python deploy.py")
    else:
        print("\n⚠️  Deployment verification found issues!")
        print("Please check the logs and fix any failing components before deployment.")
        sys.exit(1)