import pytest
from unittest.mock import patch, MagicMock
import security_monitor

class TestSecurityMonitorFrontend:
    @patch('security_monitor.requests.get')
    def test_poll_findings_triggers_notification(self, mock_get):
        # Simulate backend returning a new ML/AI finding
        mock_get.return_value.json.return_value = {
            'ml_ai_findings': [("2024-01-01 12:00:00", "Test ML/AI finding")]
        }
        frontend = security_monitor.SecurityMonitorFrontend(enable_ui=False)
        frontend._last_ml_finding = None
        frontend.backend_url = 'http://127.0.0.1:5000'
        # Patch _notify on the instance since it's not defined on the class
        from unittest.mock import MagicMock
        frontend._notify = MagicMock()
        frontend._poll_findings()
        frontend._notify.assert_called_with("ML/AI Finding", "Test ML/AI finding")
