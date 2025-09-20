import pytest
from security_monitor_backend import SecurityMonitorBackend

class TestSecurityMonitorBackend:
    def setup_method(self):
        self.backend = SecurityMonitorBackend()

    def test_ml_ai_findings_property(self):
        findings = self.backend.ml_ai_findings
        assert isinstance(findings, list)

    def test_plugin_loading(self):
        # Plugins should be loaded into self.backend.plugins or similar attribute
        assert hasattr(self.backend, 'plugins')

    def test_ml_optimize_runs(self):
        # Should not raise error
        try:
            self.backend._ml_optimize()
        except Exception as e:
            pytest.fail(f"_ml_optimize raised an exception: {e}")
