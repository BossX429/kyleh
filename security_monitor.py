
"""
Security Monitor Frontend
"""
from __future__ import annotations
import sys
import signal
import shutil
import logging
import threading
import statistics
import socket
from datetime import datetime
from pathlib import Path
from typing import Optional
import importlib.util

# Third-party imports
try:
    from plyer import notification
except ImportError:
    notification = None
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
try:
    import tkinter as tk
    from tkinter.scrolledtext import ScrolledText
except ImportError:
    tk = None
try:
    import GPUtil
except ImportError:
    GPUtil = None

# Local imports
from security_monitor_backend import SecurityMonitorBackend

# Optional ML imports
LinearRegression = None
joblib = None
try:
    from sklearn.linear_model import LinearRegression as _LR
    LinearRegression = _LR
except ImportError:
    pass
try:
    import joblib as _joblib
    joblib = _joblib
except ImportError:
    pass

def _is_module_available(module_name: str) -> bool:
    """Check if a module can be imported without actually importing it."""
    return importlib.util.find_spec(module_name) is not None
def _check_dependencies() -> tuple[bool, Optional[str]]:
    """Check if required dependencies are available.
    
    Returns:
        tuple: (success, error_message)
    """
    missing_packages = []
    
    if not _is_module_available('psutil'):
        missing_packages.append('psutil')
    
    # WMI is optional on Windows
    if sys.platform.startswith('win') and not _is_module_available('wmi'):
        print("Warning: WMI not available. Some Windows-specific features will be disabled.")
    
    if missing_packages:
        return False, f"Missing required packages: {', '.join(missing_packages)}. Install with: pip install {' '.join(missing_packages)}"
    
    return True, None

# Check dependencies early
_deps_ok, _deps_error = _check_dependencies()
if not _deps_ok:
    print(f"Error: {_deps_error}")
    sys.exit(1)

# Safe to import after dependency check
try:
    import psutil
except ImportError as e:
    print(f"Failed to import psutil: {e}")
    sys.exit(1)

# Optional WMI import for Windows
wmi = None
if sys.platform.startswith('win'):
    try:
        import wmi
    except ImportError:
        pass  # WMI is optional

import requests

# --- Frontend class (thin wrapper for UI/notifications) ---
class SecurityMonitorFrontend:
    def _show_accessibility_options(self):
        if not self.enable_ui:
            return
        import tkinter as tk
        win = tk.Toplevel(self.ui_root)
        win.title('Accessibility Options')
        win.geometry('350x180')
        tk.Label(win, text='Accessibility Settings', font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        # High contrast toggle
        hc_var = tk.BooleanVar(value=self.accessibility.get('high_contrast', False))
        def toggle_hc():
            self.accessibility['high_contrast'] = hc_var.get()
            self._apply_accessibility()
        hc_check = tk.Checkbutton(win, text='High Contrast Mode', variable=hc_var, command=toggle_hc)
        hc_check.pack(anchor='w', padx=20, pady=10)
        # Font size
        tk.Label(win, text='Font Size:').pack(anchor='w', padx=20)
        font_var = tk.IntVar(value=self.accessibility.get('font_size', 10))

        def set_font():
            self.accessibility['font_size'] = font_var.get()
            self._apply_accessibility()

        font_entry = tk.Spinbox(win, from_=8, to=24, textvariable=font_var, width=5, command=set_font)
        font_entry.pack(anchor='w', padx=20)
        # Keyboard navigation info
        tk.Label(win, text='Tab/Shift+Tab to navigate. Enter to activate.', font=("TkDefaultFont", 9)).pack(pady=10)

    def _apply_accessibility(self):
        if not self.enable_ui:
            return
        font_size = self.accessibility.get('font_size', 10)
        high_contrast = self.accessibility.get('high_contrast', False)
        fg = 'white' if high_contrast else 'black'
        bg = 'black' if high_contrast else 'white'
        if self.ui_text:
            self.ui_text.config(font=("TkDefaultFont", font_size), fg=fg, bg=bg, insertbackground=fg)
        if hasattr(self, 'fig'):
            for ax in [self.ax_cpu, self.ax_ram, self.ax_gpu, self.ax_disk, self.ax_net]:
                ax.title.set_fontsize(font_size + 1)
                ax.xaxis.label.set_fontsize(font_size)
                ax.yaxis.label.set_fontsize(font_size)
                ax.tick_params(axis='both', labelsize=font_size - 1)
            self.fig.patch.set_facecolor(bg)
            self.chart_canvas.draw()
        # Set root bg/fg
        if self.ui_root:
            self.ui_root.configure(bg=bg)
        # Save config
        try:
            import json
            with open('accessibility_config.json', 'w') as f:
                json.dump(self.accessibility, f)
        except Exception:
            pass

    def _start_findings_poll(self):
        if not self.enable_ui:
            return
        self._last_ml_finding = None
        self._poll_findings()

    def _poll_findings(self):
        import requests
        try:
            r = requests.get(f'{self.backend_url}/findings', timeout=2)
            findings = r.json().get('ml_ai_findings', [])
            if findings:
                latest = findings[-1]
                if self._last_ml_finding != latest:
                    ts, msg = latest
                    self._last_ml_finding = latest
                    self._notify("ML/AI Finding", msg)
                    self._speak(f"ML/AI finding: {msg}")
        except Exception:
            pass
        if self.ui_root:
            self.ui_root.after(5000, self._poll_findings)
    def _setup_ui(self):
        if self.enable_ui and tk is not None:
            import matplotlib
            matplotlib.use('TkAgg')
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
            self.ui_root = tk.Tk()
            self.ui_root.title('Performance Monitor')
            # Menubar with accessibility, privacy, and ML/AI findings dashboard
            menubar = tk.Menu(self.ui_root)
            self.ui_root.config(menu=menubar)
            options_menu = tk.Menu(menubar, tearoff=0)
            options_menu.add_command(label='Accessibility Options', command=self._show_accessibility_options)
            options_menu.add_command(label='Privacy Dashboard', command=self._show_privacy_dashboard)
            options_menu.add_command(label='ML/AI Findings', command=self._show_ml_findings_dashboard)
            menubar.add_cascade(label='Options', menu=options_menu)
            # Main frame for charts and log
            main_frame = tk.Frame(self.ui_root)
            main_frame.pack(fill='both', expand=True)
            # Chart area
            chart_frame = tk.Frame(main_frame)
            chart_frame.pack(side='top', fill='x', expand=False)
            self.fig = Figure(figsize=(7, 3), dpi=100)
            self.ax_cpu = self.fig.add_subplot(151)
            self.ax_ram = self.fig.add_subplot(152)
            self.ax_gpu = self.fig.add_subplot(153)
            self.ax_disk = self.fig.add_subplot(154)
            self.ax_net = self.fig.add_subplot(155)
            self.ax_cpu.set_title('CPU')
            self.ax_ram.set_title('RAM')
            self.ax_gpu.set_title('GPU')
            self.ax_disk.set_title('Disk')
            self.ax_net.set_title('Net')
            self.chart_canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
            self.chart_canvas.get_tk_widget().pack(side='top', fill='x', expand=False)
            # Log area
            self.ui_text = ScrolledText(main_frame, state='disabled', wrap='word', height=10)
            self.ui_text.pack(side='bottom', fill='both', expand=True)
            self._apply_accessibility()
            self._ui_log('Performance Monitor started.')
            self._update_charts()
            self._start_findings_poll()
        else:
            self.ui_root = None
            self.ui_text = None

    def _show_ml_findings_dashboard(self):
        if not self.enable_ui:
            return
        import tkinter as tk
        from tkinter.scrolledtext import ScrolledText
        import requests
        win = tk.Toplevel(self.ui_root)
        win.title('ML/AI Findings Dashboard')
        win.geometry('600x400')
        tk.Label(win, text='Recent ML/AI Findings (Anomalies, Adaptive Triggers)', font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        findings_box = ScrolledText(win, state='normal', wrap='word', font=("TkDefaultFont", 10))
        findings_box.pack(fill='both', expand=True, padx=10, pady=10)
        # Fetch ML/AI findings from backend
        try:
            r = requests.get(f'{self.backend_url}/findings', timeout=2)
            findings = r.json().get('ml_ai_findings', [])
            for ts, msg in findings:
                findings_box.insert('end', f'[{ts}] {msg}\n')
        except Exception:
            findings_box.insert('end', '[Error fetching ML/AI findings from backend]\n')
        findings_box.config(state='disabled')

    def _update_charts(self):
        import requests
        import numpy as np
        if not self.enable_ui or not hasattr(self, 'fig'):
            return
        try:
            r = requests.get(f'{self.backend_url}/metrics', timeout=2)
            metrics = r.json()
            # For each metric, maintain a rolling history (length 12 = 1 min at 5s interval)
            if not hasattr(self, 'chart_history'):
                self.chart_history = {
                    'cpu': [], 'ram': [], 'gpu': [], 'disk': [], 'net': []
                }
            for k in self.chart_history:
                self.chart_history[k].append(metrics.get(k, 0))
                if len(self.chart_history[k]) > 12:
                    self.chart_history[k].pop(0)
            x = np.arange(-len(self.chart_history['cpu']) + 1, 1)
            self.ax_cpu.clear()
            self.ax_cpu.set_title('CPU')
            self.ax_ram.clear()
            self.ax_ram.set_title('RAM')
            self.ax_gpu.clear()
            self.ax_gpu.set_title('GPU')
            self.ax_disk.clear()
            self.ax_disk.set_title('Disk')
            self.ax_net.clear()
            self.ax_net.set_title('Net')
            self.ax_cpu.plot(x, self.chart_history['cpu'], color='tab:red')
            self.ax_ram.plot(x, self.chart_history['ram'], color='tab:blue')
            self.ax_gpu.plot(x, self.chart_history['gpu'], color='tab:green')
            self.ax_disk.plot(x, self.chart_history['disk'], color='tab:orange')
            self.ax_net.plot(x, self.chart_history['net'], color='tab:purple')
            self.ax_cpu.set_ylim(0, 100)
            self.ax_ram.set_ylim(0, 100)
            self.ax_gpu.set_ylim(0, 100)
            self.ax_disk.set_ylim(0, max(200, max(self.chart_history['disk'] or [0]) + 10))
            self.ax_net.set_ylim(0, max(200, max(self.chart_history['net'] or [0]) + 10))
            self.chart_canvas.draw()
        except Exception:
            pass
        # Schedule next update
        if self.ui_root:
            self.ui_root.after(5000, self._update_charts)
    def _load_accessibility_config(self):
        import json
        if hasattr(self, 'accessibility_config_path') and self.accessibility_config_path.exists():
            try:
                with open(self.accessibility_config_path, 'r') as f:
                    self.accessibility.update(json.load(f))
            except Exception:
                pass
    def __init__(self, backend_url='http://127.0.0.1:5000', enable_ui: bool = True):
        self.backend_url = backend_url
        self.enable_ui = enable_ui and tk is not None
        self.ui_root = None
        self.ui_text = None
        self.accessibility = {'font_size': 10, 'high_contrast': False}
        self.privacy_findings = []
        self._init_accessibility()
        self._init_privacy_dashboard()
        if self.enable_ui:
            self._setup_ui()

    def _init_accessibility(self):
        self.accessibility_config_path = Path('accessibility_config.json')
        # Already set self.accessibility in __init__
        self._load_accessibility_config()

    def _init_privacy_dashboard(self):
        self.privacy_findings = []

    def _ui_log(self, msg=None):
        if self.enable_ui and self.ui_text:
            # Fetch latest metrics from backend
            try:
                r = requests.get(f'{self.backend_url}/metrics', timeout=2)
                metrics = r.json()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_msg = f"[{timestamp}] CPU: {metrics['cpu']}% RAM: {metrics['ram']}% GPU: {metrics['gpu']}% Disk: {metrics['disk']}MB/s Net: {metrics['net_latency']}ms/{metrics['net_jitter']}ms"
                self.ui_text.config(state='normal')
                self.ui_text.insert('end', log_msg + '\n')
                if msg:
                    self.ui_text.insert('end', f'[{timestamp}] {msg}\n')
                self.ui_text.see('end')
                self.ui_text.config(state='disabled')
            except Exception:
                pass

    def _show_privacy_dashboard(self):
        if not self.enable_ui:
            return
        win = tk.Toplevel(self.ui_root)
        win.title('Privacy Dashboard')
        win.geometry('600x400')
        tk.Label(win, text='Recent Security/Privacy Findings', font=("TkDefaultFont", 12, "bold")).pack(pady=5)
        findings_box = ScrolledText(win, state='normal', wrap='word', font=("TkDefaultFont", 10))
        findings_box.pack(fill='both', expand=True, padx=10, pady=10)
        # Fetch findings from backend
        try:
            r = requests.get(f'{self.backend_url}/findings', timeout=2)
            findings = r.json().get('findings', [])
            for ts, msg in findings:
                findings_box.insert('end', f'[{ts}] {msg}\n')
        except Exception:
            findings_box.insert('end', '[Error fetching findings from backend]\n')
        findings_box.config(state='disabled')
        # Suggestions
        tk.Label(win, text='Suggestions:', font=("TkDefaultFont", 11, "bold")).pack(pady=(10,0))
        suggestions = [
            "- Review flagged processes and connections.",
            "- Run a full antivirus scan if suspicious activity is detected.",
            "- Check camera/mic permissions in Windows settings.",
            "- Update your OS and security software regularly.",
            "- Use strong, unique passwords for all accounts."
        ]
        for s in suggestions:
            tk.Label(win, text=s, anchor='w', justify='left').pack(fill='x', padx=20)

# --- Legacy monolithic class for compatibility ---
class SecurityMonitor(SecurityMonitorBackend, SecurityMonitorFrontend):
    def __init__(self, log_file: Optional[Path] = None, enable_ui: bool = True, config_file: Optional[str] = None):
        SecurityMonitorBackend.__init__(self, log_file, config_file)
        SecurityMonitorFrontend.__init__(self, enable_ui=enable_ui)
    # --- Privacy Dashboard ---
    def _init_privacy_dashboard(self):
        self.privacy_findings = []  # List of (timestamp, message)

    def _add_privacy_finding(self, file_path):
        try:
            dest = self.integrity_quarantine_dir / (Path(file_path).name + ".quarantine")
            shutil.move(file_path, dest)
            self.logger.warning(f"Quarantined {file_path} to {dest}")
            self._ui_log(f"Quarantined {file_path} to {dest}")
            self._notify("Self-Healing", f"Quarantined {file_path} to {dest}")
            self._speak(f"Quarantined {file_path}.")
        except Exception as e:
            self.logger.error(f"Quarantine failed for {file_path}: {e}")

    def _integrity_check(self):
        """Check all files for tampering and self-heal if needed."""
        for f in self.integrity_files:
            current_hash = self._integrity_hash(f)
            if not current_hash:
                continue
            if f not in self.integrity_hashes:
                self.integrity_hashes[f] = current_hash
                continue
            if current_hash != self.integrity_hashes[f]:
                self.logger.warning(f"Integrity violation detected for {f}!")
                self._ui_log(f"Integrity violation detected for {f}!")
                self._notify("Self-Healing", f"Integrity violation detected for {f}!")
                self._speak(f"Integrity violation detected for {f}.")
                # Try to restore from backup
                self._integrity_restore(f)
                # If still mismatched, quarantine
                if self._integrity_hash(f) != self.integrity_hashes[f]:
                    self._integrity_quarantine(f)

    # Call this in __init__
    def _start_integrity_thread(self):
        def integrity_loop():
            while self.running:
                self._integrity_check()
                time.sleep(60)  # Check every 60 seconds
        t = threading.Thread(target=integrity_loop, daemon=True)
        t.start()

    # Legacy __init__ body removed; now handled by parent initializers.
        self.disk_history = []
        self.net_latency_history = []
        self.net_jitter_history = []
        self.history_length = 6  # 6*5s = 30s window
        # For optimization
        self.background_apps = [
            'OneDrive.exe', 'Dropbox.exe', 'GoogleDriveFS.exe', 'Teams.exe',
            'Skype.exe', 'Discord.exe', 'Steam.exe', 'EpicGamesLauncher.exe',
            'Battle.net.exe', 'Origin.exe', 'uplay.exe', 'Zoom.exe', 'Slack.exe',
            'chrome.exe', 'firefox.exe', 'edge.exe', 'opera.exe',
        ]
        self.optimization_cooldown = 60  # seconds
        self.last_optimization = 0

        # Initialize WMI only on Windows
        self.wmi = None
        if sys.platform.startswith('win') and wmi is not None:
            try:
                self.wmi = wmi.WMI()
                self.logger.info("WMI initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize WMI: {e}")

        # Initialize process list
        try:
            self.previous_processes = set(p.pid for p in psutil.process_iter(['pid']))
            self.logger.info(f"Initialized with {len(self.previous_processes)} processes")
        except psutil.Error as e:
            self.logger.error(f"Failed to initialize process list: {e}")
            self.previous_processes = set()

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _notify(self, title, message):
        if notification is not None:
            try:
                notification.notify(title=title, message=message, app_name="SecurityMonitor")
            except Exception:
                pass

    def _speak(self, message):
        if pyttsx3 is not None:
            try:
                if self._voice_engine is None:
                    self._voice_engine = pyttsx3.init()
                self._voice_engine.say(message)
                self._voice_engine.runAndWait()
            except Exception:
                pass

    def _load_plugins(self):
        """Discover and load plugins from the plugins directory."""
        import os
        import importlib.util
        plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        if not os.path.isdir(plugins_dir):
            return
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
        if joblib is not None:
            try:
                self.ml_model = joblib.load(self.ml_model_path)
                self.logger.info(f"Loaded ML optimization model from {self.ml_model_path}")
            except Exception:
                self.ml_model = None
    def _setup_ui(self):
        self.ui_root = tk.Tk()
        self.ui_root.title('Performance Monitor')
        self.ui_root.geometry('500x300')
        # Menubar with accessibility and privacy dashboard
        menubar = tk.Menu(self.ui_root)
        self.ui_root.config(menu=menubar)
        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label='Accessibility Options', command=self._show_accessibility_options)
        options_menu.add_command(label='Privacy Dashboard', command=self._show_privacy_dashboard)
        menubar.add_cascade(label='Options', menu=options_menu)
        self.ui_text = ScrolledText(self.ui_root, state='disabled', wrap='word')
        self.ui_text.pack(fill='both', expand=True)
        self._apply_accessibility()
        self._ui_log('Performance Monitor started.')

    def _ui_log(self, msg):
        if self.enable_ui and self.ui_text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.ui_text.config(state='normal')
            self.ui_text.insert('end', f'[{timestamp}] {msg}\n')
            self.ui_text.see('end')
            self.ui_text.config(state='disabled')
        # Also print to console for transparency
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}')
    
    def _setup_logging(self, log_file: Optional[Path] = None) -> logging.Logger:
        """Set up logging configuration.
        
        Args:
            log_file: Optional path to log file
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if log_file is None:
            log_file = Path('security_monitor.log').absolute()
        
        logger = logging.getLogger('SecurityMonitor')
        logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if already configured
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
                # Fall back to console logging
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                logger.addHandler(console_handler)
        
        return logger
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def monitor_system(self) -> None:
        """Main monitoring loop with proper error handling."""
        self.logger.info("Starting system monitoring")
        try:
            if self.enable_ui:
                self.ui_root.after(5000, self._ui_monitor_loop)  # Schedule first UI monitor loop after 5 seconds
                self.ui_root.mainloop()
            else:
                while self.running:
                    self._monitor_iteration()
                    time.sleep(5)  # Check every 5 seconds
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error in monitoring: {e}")
            raise
        finally:
            self.running = False
            self.logger.info("Monitoring stopped")

    def _ui_monitor_loop(self):
        if self.running:
            self._monitor_iteration()
            self.ui_root.after(5000, self._ui_monitor_loop)

    def _monitor_iteration(self) -> None:
        """Run one iteration of system monitoring."""
        try:
            self._check_cpu_usage()
            self._check_ram_usage()
            self._check_gpu_usage()
            self._check_disk_io()
            self._check_network_latency()
            self._detect_performance_dips()
            self._check_new_processes()
            self._check_network_connections()
            self._check_security_privacy()
            self._check_fps_input_lag()
            self._run_user_automation()
            self._ml_optimize()
        except Exception as e:
            self.logger.error(f"Error in monitoring iteration: {e}")

    def _ml_optimize(self):
        """Use ML model to predict and adjust system settings."""
        if LinearRegression is None:
            return
        # Collect features: [cpu, ram, gpu, disk, net_latency, net_jitter]
        features = [
            self.cpu_history[-1] if self.cpu_history else 0,
            self.ram_history[-1] if self.ram_history else 0,
            self.gpu_history[-1] if self.gpu_history else 0,
            self.disk_history[-1] if self.disk_history else 0,
            self.net_latency_history[-1] if self.net_latency_history else 0,
            self.net_jitter_history[-1] if self.net_jitter_history else 0,
        ]
        # Target: 1 if optimization was triggered, else 0
        last_opt = 1 if time.time() - self.last_optimization < 10 else 0
        self.ml_data.append((features, last_opt))
        # Train model if enough data
        if len(self.ml_data) > 100 and self.ml_model is None:
            X = [f for f, t in self.ml_data]
            y = [t for f, t in self.ml_data]
            self.ml_model = LinearRegression().fit(X, y)
            if joblib is not None:
                joblib.dump(self.ml_model, self.ml_model_path)
            self.logger.info("Trained ML optimization model.")
        # Use model to predict if optimization is needed
        if self.ml_model is not None:
            pred = self.ml_model.predict([features])[0]
            if pred > 0.5 and time.time() - self.last_optimization > 30:
                self._ui_log("ML-based optimization triggered.")
                self._optimize_system('ml_prediction')

    def _run_user_automation(self):
        """Run user-defined automation scripts/responses for specific games/apps."""
        if not self.user_automation:
            return
        for rule in self.user_automation.get('rules', []):
            # Example rule: {"process": "game.exe", "on": "high_cpu", "action": "script.bat"}
            proc_name = rule.get('process', '').lower()
            trigger = rule.get('on', '').lower()
            action = rule.get('action', '')
            # Check if process is running
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() == proc_name:
                        # Check trigger (for now, only high_cpu supported)
                        if trigger == 'high_cpu' and self.cpu_history and self.cpu_history[-1] > 90:
                            self._run_user_action(action, proc_name, trigger)
                except Exception:
                    continue

    def _run_user_action(self, action, proc_name, trigger):
        import subprocess
        try:
            subprocess.Popen(action, shell=True)
            msg = f"User automation: Ran '{action}' for {proc_name} on {trigger}"
            self.logger.info(msg)
            self._ui_log(msg)
        except Exception as e:
            self.logger.warning(f"Failed to run user automation action '{action}': {e}")

    def _check_fps_input_lag(self):
        """Monitor FPS and input lag (plugin-aware)."""
        plugin_metrics = []
        for plugin in self.plugins:
            try:
                metrics = plugin.get_metrics()
                if metrics:
                    plugin_metrics.append(metrics)
            except Exception as e:
                self.logger.warning(f"Plugin error: {plugin}: {e}")

        # Log plugin metrics
        for m in plugin_metrics:
            msg = f"[PLUGIN] Game: {m.get('game','?')} FPS: {m.get('fps','?')} Input Lag: {m.get('input_lag_ms','?')}ms"
            self.logger.info(msg)
            self._ui_log(msg)

        # Fallback: generic method
        try:
            if sys.platform.startswith('win'):
                import win32gui, win32api, win32con
                hwnd = win32gui.GetForegroundWindow()
                start = time.time()
                win32api.PostMessage(hwnd, win32con.WM_NULL, 0, 0)
                lag = (time.time() - start) * 1000
                fps = 60  # Assume 60Hz as default
                if lag > 50:
                    msg = f"High input lag detected: {lag:.1f}ms (window: {hwnd})"
                    self.logger.warning(msg)
                    self._ui_log(msg)
                self.logger.info(f"Estimated FPS: {fps}, Input lag: {lag:.1f}ms")
        except Exception as e:
            self.logger.debug(f"FPS/input lag monitoring not available: {e}")

    def _check_security_privacy(self):
        """Monitor for suspicious processes, unauthorized network connections, and privacy risks."""
        suspicious_names = [
            'xmrig', 'minerd', 'powershell.exe', 'cmd.exe', 'pythonw.exe',
            'svchosts.exe', 'taskhostw.exe', 'winlogon.exe', 'lsasss.exe',
            'rundll32.exe', 'conhost.exe', 'explorer.exe', 'mshta.exe',
            'wscript.exe', 'cscript.exe', 'regsvr32.exe', 'schtasks.exe',
            'TeamViewer.exe', 'AnyDesk.exe', 'ngrok.exe', 'putty.exe',
            'ncat.exe', 'nc.exe', 'telnet.exe', 'plink.exe', 'ssh.exe',
        ]
        flagged = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
            try:
                pname = proc.info['name'].lower()
                if any(s in pname for s in suspicious_names):
                    flagged.append(f"Suspicious process: {proc.info['name']} (PID {proc.info['pid']}, User {proc.info['username']})")
            except Exception:
                continue
        # Unauthorized network connections (non-local, non-browser, non-game)
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    if not (conn.raddr.ip.startswith('127.') or conn.raddr.ip.startswith('::1') or conn.raddr.ip.startswith('192.168.') or conn.raddr.ip.startswith('10.') or conn.raddr.ip.startswith('172.')):
                        try:
                            pname = psutil.Process(conn.pid).name().lower() if conn.pid else ''
                        except Exception:
                            pname = ''
                        if not any(x in pname for x in ['chrome', 'firefox', 'edge', 'opera', 'steam', 'epic', 'battle', 'game', 'discord']):
                            flagged.append(f"Unauthorized external connection: {pname} (PID {conn.pid}) {conn.laddr.ip}:{conn.laddr.port} -> {conn.raddr.ip}:{conn.raddr.port}")
        except Exception:
            pass
        # Privacy risk: processes accessing webcam/mic (Windows only, basic)
        if sys.platform.startswith('win') and self.wmi:
            try:
                cams = self.wmi.query("SELECT * FROM Win32_PnPEntity WHERE Description LIKE '%Camera%'")
                if cams:
                    flagged.append("Camera device detected (check for unauthorized access)")
            except Exception:
                pass
        # Log all flagged items
        for item in flagged:
            self.logger.warning(f"SECURITY/PRIVACY: {item}")
            self._ui_log(f"SECURITY/PRIVACY: {item}")
            self._add_privacy_finding(item)
            self._notify("Security/Privacy Alert", item)
            self._speak(f"Security or privacy alert: {item}")

    def _check_cpu_usage(self) -> None:
        """Monitor CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_history.append(cpu_percent)
            if len(self.cpu_history) > self.history_length:
                self.cpu_history.pop(0)
            if cpu_percent > 90:
                msg = f"High CPU usage detected: {cpu_percent}%"
                self.logger.warning(msg)
                self._notify("High CPU Usage", msg)
                self._speak(msg)
        except Exception as e:
            self.logger.error(f"Error monitoring CPU: {e}")

    def _check_ram_usage(self) -> None:
        """Monitor RAM usage."""
        try:
            mem = psutil.virtual_memory()
            self.ram_history.append(mem.percent)
            if len(self.ram_history) > self.history_length:
                self.ram_history.pop(0)
            if mem.percent > 90:
                msg = f"High RAM usage detected: {mem.percent}% ({mem.used // (1024**2)}MB/{mem.total // (1024**2)}MB)"
                self.logger.warning(msg)
                self._notify("High RAM Usage", msg)
                self._speak(msg)
        except Exception as e:
            self.logger.error(f"Error monitoring RAM: {e}")

    def _check_gpu_usage(self) -> None:
        """Monitor GPU usage (if available)."""
        if GPUtil is None:
            return
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                avg_load = sum([gpu.load*100 for gpu in gpus]) / len(gpus)
                if avg_load > 90:
                    msg = f"High GPU usage detected: {avg_load:.1f}%"
                    self.logger.warning(msg)
                    self._notify("High GPU Usage", msg)
                    self._speak(msg)
                self.gpu_history.append(avg_load)
                if len(self.gpu_history) > self.history_length:
                    self.gpu_history.pop(0)
                for gpu in gpus:
                    if gpu.load * 100 > 90:
                        self.logger.warning(f"High GPU usage detected: {gpu.name} {gpu.load*100:.1f}% (Memory: {gpu.memoryUsed}MB/{gpu.memoryTotal}MB)")
        except Exception as e:
            self.logger.error(f"Error monitoring GPU: {e}")

    def _detect_performance_dips(self) -> None:
        """Detect sudden dips or spikes in CPU, RAM, or GPU usage."""
        # CPU
        if len(self.cpu_history) == self.history_length:
            avg = sum(self.cpu_history[:-1]) / (self.history_length-1)
            latest = self.cpu_history[-1]
            if abs(latest - avg) > 30 and latest > 60:
                msg = f"Sudden CPU usage change detected: {avg:.1f}% -> {latest:.1f}%"
                self.logger.warning(msg)
                self._ui_log(msg)
                self._optimize_system('cpu')
            # Predictive: warn if trend is rising fast
            if statistics.stdev(self.cpu_history) > 15 and latest > 70:
                msg = f"Predictive: CPU usage volatility detected (stddev={statistics.stdev(self.cpu_history):.1f}%)"
                self.logger.warning(msg)
                self._ui_log(msg)
        # RAM
        if len(self.ram_history) == self.history_length:
            avg = sum(self.ram_history[:-1]) / (self.history_length-1)
            latest = self.ram_history[-1]
            if abs(latest - avg) > 20 and latest > 70:
                msg = f"Sudden RAM usage change detected: {avg:.1f}% -> {latest:.1f}%"
                self.logger.warning(msg)
                self._ui_log(msg)
                self._optimize_system('ram')
            if statistics.stdev(self.ram_history) > 10 and latest > 70:
                msg = f"Predictive: RAM usage volatility detected (stddev={statistics.stdev(self.ram_history):.1f}%)"
                self.logger.warning(msg)
                self._ui_log(msg)
        # GPU
        if len(self.gpu_history) == self.history_length:
            avg = sum(self.gpu_history[:-1]) / (self.history_length-1)
            latest = self.gpu_history[-1]
            if abs(latest - avg) > 30 and latest > 60:
                msg = f"Sudden GPU usage change detected: {avg:.1f}% -> {latest:.1f}%"
                self.logger.warning(msg)
                self._ui_log(msg)
                self._optimize_system('gpu')
            if statistics.stdev(self.gpu_history) > 15 and latest > 60:
                msg = f"Predictive: GPU usage volatility detected (stddev={statistics.stdev(self.gpu_history):.1f}%)"
                self.logger.warning(msg)
                self._ui_log(msg)
        # Disk I/O
        if len(self.disk_history) == self.history_length:
            avg = sum(self.disk_history[:-1]) / (self.history_length-1)
            latest = self.disk_history[-1]
            if abs(latest - avg) > 50 and latest > 100:
                msg = f"Sudden Disk I/O change detected: {avg:.1f}MB/s -> {latest:.1f}MB/s"
                self.logger.warning(msg)
                self._ui_log(msg)
            if statistics.stdev(self.disk_history) > 40 and latest > 100:
                msg = f"Predictive: Disk I/O volatility detected (stddev={statistics.stdev(self.disk_history):.1f}MB/s)"
                self.logger.warning(msg)
                self._ui_log(msg)
        # Network latency/jitter
        if len(self.net_latency_history) == self.history_length:
            avg = sum(self.net_latency_history[:-1]) / (self.history_length-1)
            latest = self.net_latency_history[-1]
            if abs(latest - avg) > 50 and latest > 100:
                msg = f"Sudden network latency change detected: {avg:.1f}ms -> {latest:.1f}ms"
                self.logger.warning(msg)
                self._ui_log(msg)
            if statistics.stdev(self.net_latency_history) > 40 and latest > 100:
                msg = f"Predictive: Network latency volatility detected (stddev={statistics.stdev(self.net_latency_history):.1f}ms)"
                self.logger.warning(msg)
                self._ui_log(msg)
        if len(self.net_jitter_history) == self.history_length:
            avg = sum(self.net_jitter_history[:-1]) / (self.history_length-1)
            latest = self.net_jitter_history[-1]
            if abs(latest - avg) > 20 and latest > 30:
                msg = f"Sudden network jitter change detected: {avg:.1f}ms -> {latest:.1f}ms"
                self.logger.warning(msg)
                self._ui_log(msg)
            if statistics.stdev(self.net_jitter_history) > 15 and latest > 30:
                msg = f"Predictive: Network jitter volatility detected (stddev={statistics.stdev(self.net_jitter_history):.1f}ms)"
                self.logger.warning(msg)
                self._ui_log(msg)

    def _check_disk_io(self):
        try:
            disk_counters = psutil.disk_io_counters()
            # MB/s over last 5s (approximate)
            read_mb = disk_counters.read_bytes / (1024*1024)
            write_mb = disk_counters.write_bytes / (1024*1024)
            total_mb = read_mb + write_mb
            self.disk_history.append(total_mb)
            if len(self.disk_history) > self.history_length:
                self.disk_history.pop(0)
            if total_mb > 200:
                msg = f"High disk I/O detected: {total_mb:.1f}MB/s (Read: {read_mb:.1f}, Write: {write_mb:.1f})"
                self.logger.warning(msg)
                self._ui_log(msg)
        except Exception as e:
            self.logger.error(f"Error monitoring disk I/O: {e}")

    def _check_network_latency(self):
        try:
            # Ping google DNS
            host = '8.8.8.8'
            port = 53
            latencies = []
            for _ in range(3):
                start = time.time()
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect((host, port))
                    s.close()
                    latency = (time.time() - start) * 1000
                    latencies.append(latency)
                except Exception:
                    latencies.append(1000)
            avg_latency = sum(latencies) / len(latencies)
            jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0
            self.net_latency_history.append(avg_latency)
            self.net_jitter_history.append(jitter)
            if len(self.net_latency_history) > self.history_length:
                self.net_latency_history.pop(0)
            if len(self.net_jitter_history) > self.history_length:
                self.net_jitter_history.pop(0)
            if avg_latency > 150:
                msg = f"High network latency detected: {avg_latency:.1f}ms (jitter: {jitter:.1f}ms)"
                self.logger.warning(msg)
                self._ui_log(msg)
        except Exception as e:
            self.logger.error(f"Error monitoring network latency: {e}")

    def _optimize_system(self, reason):
        now = time.time()
        if now - self.last_optimization < self.optimization_cooldown:
            self._ui_log('Optimization skipped (cooldown active).')
            return
        self.last_optimization = now
        actions = []
        # 1. Close background apps
        closed = self._close_background_apps()
        if closed:
            actions.append(f'Closed: {", ".join(closed)}')
        # 2. Boost foreground/game process priority
        boosted = self._boost_foreground_priority()
        if boosted:
            actions.append(f'Boosted: {boosted}')
        # 3. Attempt to clear RAM (Windows only, safe method)
        if sys.platform.startswith('win'):
            cleared = self._clear_ram_windows()
            if cleared:
                actions.append('Requested RAM clear')
        msg = f'Optimization actions: {"; ".join(actions) if actions else "None"}'
        self.logger.info(f"Optimization actions taken: {actions if actions else 'None'} (Reason: {reason})")
        self._ui_log(f"Optimization actions taken: {actions if actions else 'None'} (Reason: {reason})")
        self._notify("System Optimization", msg)
        self._speak(f"System optimization performed. {msg}")

    def _close_background_apps(self):
        closed = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in self.background_apps:
                    proc.terminate()
                    closed.append(proc.info['name'])
            except Exception:
                continue
        return closed

    def _boost_foreground_priority(self):
        # Windows only: boost foreground window process priority
        if not sys.platform.startswith('win'):
            return None
        try:
            import ctypes
            import win32process
            import win32gui
            import win32con
            hwnd = win32gui.GetForegroundWindow()
            tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            proc.nice(psutil.HIGH_PRIORITY_CLASS)
            return proc.name() if proc else None
        except Exception:
            return None

    def _clear_ram_windows(self):
        # Use Windows API to empty standby list (safe, no admin required)
        try:
            import ctypes
            ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
            return True
        except Exception:
            return False

    def _check_new_processes(self) -> None:
        """Monitor for new processes."""
        try:
            current_processes = set(p.pid for p in psutil.process_iter(['pid']))
            new_processes = current_processes - self.previous_processes
            
            for pid in new_processes:
                try:
                    process = psutil.Process(pid)
                    with process.oneshot():  # More efficient process info gathering
                        proc_info = {
                            'name': process.name(),
                            'exe': process.exe() if process.exe() else 'N/A',
                            'cmdline': ' '.join(process.cmdline()) if process.cmdline() else 'N/A',
                            'username': process.username() if process.username() else 'N/A',
                            'create_time': datetime.fromtimestamp(process.create_time())
                        }
                        self.logger.info(f"New process detected: PID={pid}, Name={proc_info['name']}, User={proc_info['username']}")
                        self.logger.debug(f"Process details: {proc_info}")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.debug(f"Could not access process {pid}: {e}")
                except Exception as e:
                    self.logger.error(f"Error checking process {pid}: {e}")

            self.previous_processes = current_processes
        except Exception as e:
            self.logger.error(f"Error monitoring processes: {e}")

    def _check_network_connections(self) -> None:
        """Monitor network connections (filtering for suspicious activity)."""
        try:
            connections = psutil.net_connections(kind='inet')
            suspicious_ports = {22, 23, 135, 139, 445, 1433, 3389, 5432, 5900}  # Common attack targets
            external_connections = []
            
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    # Filter for external connections (not localhost)
                    if not (conn.raddr.ip.startswith('127.') or 
                           conn.raddr.ip.startswith('::1') or
                           conn.raddr.ip.startswith('192.168.') or
                           conn.raddr.ip.startswith('10.') or
                           conn.raddr.ip.startswith('172.')):
                        external_connections.append(conn)
                    
                    # Log suspicious port activity
                    if conn.laddr.port in suspicious_ports or (conn.raddr and conn.raddr.port in suspicious_ports):
                        self.logger.warning(
                            f"Suspicious port activity: {conn.laddr.ip}:{conn.laddr.port} -> "
                            f"{conn.raddr.ip}:{conn.raddr.port} (PID: {conn.pid})"
                        )
            
            # Log summary of external connections instead of individual ones
            if external_connections:
                self.logger.info(f"Active external connections: {len(external_connections)}")
                # Log details for first few connections to avoid spam
                for conn in external_connections[:3]:
                    self.logger.debug(
                        f"External connection: {conn.laddr.ip}:{conn.laddr.port} -> "
                        f"{conn.raddr.ip}:{conn.raddr.port} (PID: {conn.pid})"
                    )
                if len(external_connections) > 3:
                    self.logger.debug(f"... and {len(external_connections) - 3} more external connections")
                    
        except psutil.AccessDenied:
            self.logger.warning("Access denied when checking network connections")
        except Exception as e:
            self.logger.error(f"Error monitoring network: {e}")


def main() -> None:
    """Main entry point for the security monitor (backend/frontend separation)."""
    print("Performance monitoring started. Backend/frontend separation mode.")
    print("Press Ctrl+C to stop monitoring.")
    try:
        backend = SecurityMonitorBackend()
        frontend = SecurityMonitorFrontend(enable_ui=True)
        if frontend.enable_ui and frontend.ui_root is not None:
            frontend.ui_root.after(5000, frontend._ui_log)  # Schedule first UI log
            frontend.ui_root.mainloop()
        else:
            while backend.running:
                time.sleep(5)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()