from __future__ import annotations
from security_monitor_backend_api import SecurityMonitorBackendAPI
import sys
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Set
try:
    import psutil
except ImportError as e:
    print(f"Failed to import psutil: {e}")
    sys.exit(1)
wmi = None
if sys.platform.startswith('win'):
    try:
        import wmi
    except ImportError:
        pass  # WMI is optional

    # --- Advanced ML/AI Optimization Enhancements ---
    def _init_ml_ai(self):
        # Try to import IsolationForest for anomaly detection
        try:
            from sklearn.ensemble import IsolationForest
            self.IsolationForest = IsolationForest
        except ImportError:
            self.IsolationForest = None
        self.anomaly_model = None
        self.anomaly_scores = []
        self.ml_findings = []
        self._ml_ai_last_retrain = time.time()

    def _ml_ai_update(self):
        # Collect features for anomaly detection
        features = [
            self.cpu_history[-1] if self.cpu_history else 0,
            self.ram_history[-1] if self.ram_history else 0,
            self.gpu_history[-1] if self.gpu_history else 0,
            self.disk_history[-1] if self.disk_history else 0,
            self.net_latency_history[-1] if self.net_latency_history else 0,
            self.net_jitter_history[-1] if self.net_jitter_history else 0
        ]
        # --- Anomaly Detection ---
        if self.IsolationForest is not None and len(self.ml_data) > 30:
            # Retrain model every 10 minutes or if not trained
            if (
                self.anomaly_model is None or
                (time.time() - self._ml_ai_last_retrain > 600)
            ):
                X = [f for f, _ in self.ml_data]
                self.anomaly_model = self.IsolationForest(
                    contamination=0.1, random_state=42
                )
                self.anomaly_model.fit(X)
                self._ml_ai_last_retrain = time.time()
            # Predict anomaly score for current features
            try:
                score = self.anomaly_model.decision_function([
                    features
                ])[0]
                self.anomaly_scores.append(score)
                if len(self.anomaly_scores) > 100:
                    self.anomaly_scores.pop(0)
                # If anomaly detected (score below threshold), log finding
                if score < -0.1:
                    msg = (
                        f"Anomaly detected in system metrics "
                        f"(score={score:.2f})"
                    )
                    self.ml_findings.append(
                        (
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            msg
                        )
                    )
                    self.logger.warning(msg)
            except Exception as e:
                self.logger.debug(f"Anomaly detection error: {e}")

        # --- Adaptive Thresholds for Optimization ---
        # Use rolling mean/stddev for CPU, RAM, GPU
        adaptive = {}
        for name, hist in zip(
            ['cpu', 'ram', 'gpu'],
            [self.cpu_history, self.ram_history, self.gpu_history]
        ):
            if len(hist) >= self.history_length:
                mean = sum(hist) / len(hist)
                std = (
                    sum((x - mean) ** 2 for x in hist) / len(hist)
                ) ** 0.5
                adaptive[name] = {
                    'mean': mean,
                    'std': std
                }
        self.adaptive_thresholds = adaptive

    @property
    def ml_ai_findings(self):
        # Return last 20 ML/AI findings
        return self.ml_findings[-20:]  # Ensure line length is acceptable

    def _setup_logging(self, log_file: Optional[Path] = None) -> logging.Logger:
        if log_file is None:
            log_file = Path('security_monitor.log').absolute()
        logger = logging.getLogger('SecurityMonitor')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.INFO)
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                logger.info(f"Logging initialized to {log_file}")
            except Exception as e:
                print(f"Failed to set up file logging: {e}")
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                logger.addHandler(console_handler)
        return logger

    def __init__(self, log_file: Optional[Path] = None, config_file: Optional[str] = None):
        self._init_ml_ai()
        self.running: bool = True
        self.logger = self._setup_logging(log_file)
        self.ml_data = []
        self.ml_model = None
        self.ml_model_path = 'ml_optimization_model.pkl'
        self.plugins = []
        self._load_plugins()
        self._init_integrity()
        self._start_integrity_thread()
        self._init_auto_update()
        self._start_update_thread()
        self.previous_processes: Set[int] = set()
        self.user_automation = {}
        if config_file:
            self._load_user_automation(config_file)
        self._load_ml_model()
        self.cpu_history = []
        self.ram_history = []
        self.gpu_history = []
        self.disk_history = []
        self.net_latency_history = []
        self.net_jitter_history = []
        self.history_length = 6
        self.background_apps = [
            'OneDrive.exe', 'Dropbox.exe', 'GoogleDriveFS.exe', 'Teams.exe',
            'Skype.exe', 'Discord.exe', 'Steam.exe', 'EpicGamesLauncher.exe',
            'Battle.net.exe', 'Origin.exe', 'uplay.exe', 'Zoom.exe',
            'Slack.exe', 'chrome.exe', 'firefox.exe', 'edge.exe',
            'opera.exe'
        ]
        self.optimization_cooldown = 60
        self.last_optimization = 0
        self.privacy_findings = []
        self.wmi = None
        if sys.platform.startswith('win') and wmi is not None:
            try:
                self.wmi = wmi.WMI()
                self.logger.info("WMI initialized successfully")
            except Exception as e:
                self.logger.warning(
                    f"Failed to initialize WMI: {e}"
                )
        try:
            self.previous_processes = set(
                p.pid for p in psutil.process_iter(['pid'])
            )
            self.logger.info(
                f"Initialized with {len(self.previous_processes)} processes"
            )
        except psutil.Error as e:
            self.logger.error(
                f"Failed to initialize process list: {e}"
            )
            self.previous_processes = set()
        # Start API server after all initializations
        self.api_server = SecurityMonitorBackendAPI(self)
        self.api_server.start()

    def _notify(self, title, message):
        from plyer import notification
        if notification is not None:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="SecurityMonitor"
                )
            except Exception:
                pass

    def _speak(self, message):
        import pyttsx3
        if pyttsx3 is not None:
            try:
                if not hasattr(self, '_voice_engine') or self._voice_engine is None:
                    self._voice_engine = pyttsx3.init()
                self._voice_engine.say(message)
                self._voice_engine.runAndWait()
            except Exception:
                pass

    def _load_plugins(self):
        import os
        import importlib.util
        # self.background_apps assignment is in __init__
        # ...rest of function unchanged...
        for fname in os.listdir(plugins_dir):
            if fname.endswith('.py') and not fname.startswith('_'):
                fpath = os.path.join(plugins_dir, fname)
                spec = importlib.util.spec_from_file_location(fname[:-3], fpath)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(mod)
                        if hasattr(mod, 'get_metrics'):
                            self.plugins.append(mod)
                            self.logger.info(f"Loaded plugin: {fname}")
                    except Exception as e:
                        self.logger.warning(f"Failed to load plugin {fname}: {e}")

    
    def _load_ml_model(self):
        try:
            import joblib
            self.ml_model = joblib.load(self.ml_model_path)
            self.logger.info(
                f"Loaded ML optimization model from {self.ml_model_path}"
            )
        except Exception:
            self.ml_model = None
    def _ml_optimize(self):
        # Use ML model to predict and adjust system settings, and call anomaly/adaptive logic
        self._ml_ai_update()
        # --- Existing ML logic (linear regression) ---
        try:
            from sklearn.linear_model import LinearRegression
        except ImportError:
            LinearRegression = None
        features = [
            self.cpu_history[-1] if self.cpu_history else 0,
            self.ram_history[-1] if self.ram_history else 0,
            self.gpu_history[-1] if self.gpu_history else 0,
            self.disk_history[-1] if self.disk_history else 0,
            self.net_latency_history[-1] if self.net_latency_history else 0,
            self.net_jitter_history[-1] if self.net_jitter_history else 0
        ]
        last_opt = 1 if time.time() - self.last_optimization < 10 else 0
        self.ml_data.append((features, last_opt))
        if (
            len(self.ml_data) > 100 and
            self.ml_model is None and
            LinearRegression is not None
        ):
            X = [f for f, t in self.ml_data]
            y = [t for f, t in self.ml_data]
            self.ml_model = LinearRegression().fit(X, y)
            try:
                import joblib
                joblib.dump(self.ml_model, self.ml_model_path)
            except Exception:
                pass
            self.logger.info(
                "Trained ML optimization model."
            )
        # Use model to predict if optimization is needed
        if self.ml_model is not None:
            pred = self.ml_model.predict([features])[0]
            if pred > 0.5 and time.time() - self.last_optimization > 30:
                self.logger.info(
                    "ML-based optimization triggered."
                )
                self._optimize_system('ml_prediction')
        # --- Adaptive threshold triggers ---
        for name, hist in zip(
            ['cpu', 'ram', 'gpu'],
            [self.cpu_history, self.ram_history, self.gpu_history]
        ):
            if len(hist) >= self.history_length and name in self.adaptive_thresholds:
                mean = self.adaptive_thresholds[name]['mean']
                std = self.adaptive_thresholds[name]['std']
                latest = hist[-1]
                # If value is more than 2 std above mean, trigger optimization
                if (
                    latest > mean + 2 * std and
                    time.time() - self.last_optimization > 30
                ):
                    msg = (
                        f"Adaptive threshold optimization triggered for {name.upper()} "
                        f"(value={latest:.1f}, mean={mean:.1f}, std={std:.1f})"
                    )
                    self.logger.info(msg)
                    self._optimize_system(f'adaptive_{name}')

    def _init_integrity(self):
        self.integrity_files = [__file__]
        self.integrity_hashes = {}
        self.integrity_backup_dir = Path('backup_integrity')
        self.integrity_quarantine_dir = Path('quarantine')
        self.integrity_backup_dir.mkdir(exist_ok=True)
        self.integrity_quarantine_dir.mkdir(exist_ok=True)
        self._integrity_hash_all()
        self._integrity_backup_all()

    def _integrity_hash(self, file_path):
        import hashlib
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            return hashlib.sha256(data).hexdigest()
        except Exception as e:
            self.logger.error(f"Hashing failed for {file_path}: {e}")
            return None

    def _integrity_hash_all(self):
        for f in self.integrity_files:
            h = self._integrity_hash(f)
            if h:
                self.integrity_hashes[f] = h

    def _integrity_backup(self, file_path):
        import shutil
        try:
            dest = self.integrity_backup_dir / Path(file_path).name
            shutil.copy2(file_path, dest)
            self.logger.info(
                f"Backed up {file_path} to {dest}"
            )
        except Exception as e:
            self.logger.error(f"Backup failed for {file_path}: {e}")

    def _integrity_backup_all(self):
        for f in self.integrity_files:
            self._integrity_backup(f)

    def _integrity_restore(self, file_path):
        import shutil
        try:
            backup = self.integrity_backup_dir / Path(file_path).name
            if backup.exists():
                shutil.copy2(backup, file_path)
                self.logger.warning(
                    f"Restored {file_path} from backup!"
                )
                self._notify(
                    "Self-Healing",
                    f"Restored {file_path} from backup!"
                )
                self._speak(
                    f"Restored {file_path} from backup."
                )
        except Exception as e:
            self.logger.error(f"Restore failed for {file_path}: {e}")

    def _integrity_quarantine(self, file_path):
        import shutil
        try:
            dest = self.integrity_quarantine_dir / (Path(file_path).name + ".quarantine")
            shutil.move(file_path, dest)
            self.logger.warning(
                f"Quarantined {file_path} to {dest}"
            )
            self._notify(
                "Self-Healing",
                f"Quarantined {file_path} to {dest}"
            )
            self._speak(
                f"Quarantined {file_path}."
            )
        except Exception as e:
            self.logger.error(f"Quarantine failed for {file_path}: {e}")

    def _integrity_check(self):
        for f in self.integrity_files:
            current_hash = self._integrity_hash(f)
            if not current_hash:
                continue
            if f not in self.integrity_hashes:
                self.integrity_hashes[f] = current_hash
                continue
            if current_hash != self.integrity_hashes[f]:
                self.logger.warning(
                    f"Integrity violation detected for {f}!"
                )
                self._notify(
                    "Self-Healing",
                    f"Integrity violation detected for {f}!"
                )
                self._speak(
                    f"Integrity violation detected for {f}."
                )
                self._integrity_restore(f)
                if self._integrity_hash(f) != self.integrity_hashes[f]:
                    self._integrity_quarantine(f)

    def _start_integrity_thread(self):
        def integrity_loop():
            while self.running:
                self._integrity_check()
                time.sleep(60)
        t = threading.Thread(target=integrity_loop, daemon=True)
        t.start()

    def _init_auto_update(self):
        self.update_manifest_path = Path('update_manifest.json')
        self.update_dir = Path('pending_update')
        self.update_dir.mkdir(exist_ok=True)
        self.current_version = self._get_current_version()

    def _get_current_version(self):
        return '1.0.0'

    def _check_for_update(self):
        import json
        if not self.update_manifest_path.exists():
            return
        try:
            with open(self.update_manifest_path, 'r') as f:
                manifest = json.load(f)
            new_version = manifest.get('version')
            update_zip = manifest.get('update_zip')
            if new_version and update_zip and new_version != self.current_version:
                self.logger.info(
                    f"Update available: {new_version}"
                )
                self._notify("Update Available", f"Version {new_version} ready to install.")
                self._speak(f"Update available. Version {new_version} ready to install.")
                self._download_and_stage_update(update_zip)
        except Exception as e:
            self.logger.error(f"Failed to check for update: {e}")

    def _download_and_stage_update(self, update_zip):
        import shutil
        import zipfile
        try:
            src = Path(update_zip)
            if not src.exists():
                self.logger.error(f"Update zip not found: {src}")
                return
            dest = self.update_dir / src.name
            shutil.copy2(src, dest)
            with zipfile.ZipFile(dest, 'r') as zip_ref:
                zip_ref.extractall(self.update_dir)
            self.logger.info(
                f"Update staged in {self.update_dir}"
            )
            self._notify(
                "Update Staged",
                f"Update staged in {self.update_dir}. Restart to apply."
            )
            self._speak(
                "Update staged. Restart to apply."
            )
        except Exception as e:
            self.logger.error(f"Failed to stage update: {e}")

    def _apply_staged_update(self):
        import shutil
    # import os  # F401: remove unused import
        try:
            if not any(self.update_dir.iterdir()):
                return
            for item in self.update_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, Path(item.name))
            self.logger.info(
                "Update applied. Please restart the application."
            )
            self._notify(
                "Update Applied",
                "Update applied. Please restart."
            )
            self._speak(
                "Update applied. Please restart."
            )
            for item in self.update_dir.iterdir():
                if item.is_file():
                    item.unlink()
        except Exception as e:
            self.logger.error(f"Failed to apply update: {e}")


    def _start_update_thread(self):
        def update_loop():
            while self.running:
                self._check_for_update()
                time.sleep(3600)
        t = threading.Thread(target=update_loop, daemon=True)
        t.start()

    def _load_user_automation(self, config_file):
        import json
        try:
            with open(config_file, 'r') as f:
                self.user_automation = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load user automation config: {e}")
            self.logger.error(f"Failed to load user automation config: {e}")
