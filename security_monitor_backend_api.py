# Flask API server for SecurityMonitorBackend
from flask import Flask, jsonify, request
from threading import Thread

class SecurityMonitorBackendAPI:
    def __init__(self, backend):
        self.backend = backend
        self.app = Flask(__name__)
        self._setup_routes()
        self.thread = None

    def _setup_routes(self):
        @self.app.route('/metrics', methods=['GET'])
        def get_metrics():
            return jsonify({
                'cpu': self.backend.cpu_history[-1] if self.backend.cpu_history else 0,
                'ram': self.backend.ram_history[-1] if self.backend.ram_history else 0,
                'gpu': self.backend.gpu_history[-1] if self.backend.gpu_history else 0,
                'disk': self.backend.disk_history[-1] if self.backend.disk_history else 0,
                'net_latency': self.backend.net_latency_history[-1] if self.backend.net_latency_history else 0,
                'net_jitter': self.backend.net_jitter_history[-1] if self.backend.net_jitter_history else 0,
            })

        @self.app.route('/findings', methods=['GET'])
        def get_findings():
            return jsonify({'findings': self.backend.privacy_findings})

        @self.app.route('/optimize', methods=['POST'])
        def post_optimize():
            self.backend._optimize_system('api_request')
            return jsonify({'status': 'ok'})

        @self.app.route('/plugins', methods=['GET'])
        def get_plugins():
            plugin_metrics = []
            for plugin in self.backend.plugins:
                try:
                    metrics = plugin.get_metrics()
                    if metrics:
                        plugin_metrics.append(metrics)
                except Exception:
                    continue
            return jsonify({'plugins': plugin_metrics})

        @self.app.route('/automation', methods=['GET'])
        def get_automation():
            return jsonify({'automation': self.backend.user_automation})

        @self.app.route('/automation/run', methods=['POST'])
        def post_automation_run():
            self.backend._run_user_automation()
            return jsonify({'status': 'ok'})

        @self.app.route('/state', methods=['GET'])
        def get_state():
            return jsonify({
                'running': self.backend.running,
                'version': self.backend.current_version
            })

    def start(self, host='127.0.0.1', port=5000):
        def run():
            self.app.run(host=host, port=port, threaded=True)
        self.thread = Thread(target=run, daemon=True)
        self.thread.start()
