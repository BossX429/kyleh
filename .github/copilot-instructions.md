
# Copilot Instructions for Security Monitor & SecurityBot Codebase

## Architecture Overview
- **SecurityMonitor**: Modular Python app with backend (`SecurityMonitorBackend`), frontend (`SecurityMonitorFrontend`), and legacy CLI (`SecurityMonitor`).
	- **Backend**: System/resource monitoring, ML/AI anomaly detection (IsolationForest, LinearRegression), self-healing, plugin loading, Flask API (`security_monitor_backend.py`, `security_monitor_backend_api.py`).
	- **Frontend**: Tkinter UI (optional), notifications, accessibility, privacy dashboards. Communicates with backend via HTTP (`security_monitor.py`).
	- **Plugins**: Drop-in Python files with `get_metrics()` in `plugins/` auto-load at runtime.
	- **API**: Flask server exposes `/metrics`, `/findings`, `/optimize`, `/plugins`, `/automation`, `/state` endpoints.
- **SecurityBot**: Enterprise security orchestration (see `SecurityBot/`).
	- **Main**: `security_bot_main.py` orchestrates all components (threat detection, alerting, reporting, REST API, UI/UX, database, authentication).
	- **Component pattern**: Each major feature (e.g., `threat_detection.py`, `alerting_system.py`, `reporting_system.py`) is a class with its own logging and config.
	- **REST API**: Flask-based, JWT auth, integrates all components (`rest_api.py`).
	- **Deployment**: Automated via `deploy.py`, with verification scripts (`deployment_verification.py`, `deployment_verification_simple.py`).

## Developer Workflows
- **Install**: `python -m pip install .` (dev: `python -m pip install -e .[dev]`)
- **Run SecurityMonitor**: `python security_monitor.py` (UI+backend) or `python system_monitor/monitor.py` (CLI)
- **Run SecurityBot**: `python SecurityBot/security_bot_main.py` (or use deployment scripts)
- **Test**: `pytest` (see `tests/`), or run `SecurityBot/deployment_verification*.py` for integration checks
- **Format**: `black .` and `isort .` (see `pyproject.toml`)
- **Type check**: `mypy .` or strict Pyright config
- **Dependencies**: Declared in `pyproject.toml` (see `[project]` and `[project.optional-dependencies]`)

## Project Conventions
- **Strict type checking**: Enforced via mypy/pyright (`pyproject.toml`).
- **Logging**: Each component/class sets up its own logger. Main logs: `security_monitor.log`, `logs/` (SecurityBot).
- **ML/AI**: scikit-learn for anomaly detection/optimization. Models retrained periodically, persisted as `ml_optimization_model.pkl`.
- **Self-healing**: Integrity checks, auto-restore/quarantine for monitored files (see `_integrity_*` methods).
- **User automation**: User-defined automation rules via config (see `_load_user_automation`).
- **Accessibility**: UI supports high-contrast mode, font scaling (`_apply_accessibility`).
- **Windows-specific**: WMI features if `wmi` is installed; some optimizations are Windows-only.
- **Component pattern**: SecurityBot classes are single-responsibility, each with `setup_logging()` and config/init methods.

## Integration Points
- **SecurityMonitor Flask API**: Used by frontend/UI and for automation/testing.
- **SecurityBot REST API**: JWT auth, integrates all components, see `rest_api.py`.
- **Plugins**: Drop `.py` files with `get_metrics()` in `plugins/` to extend monitoring.
- **Notifications**: `plyer` (desktop), `pyttsx3` (speech, optional), multi-channel alerting in SecurityBot.

## Key Files/Directories
- `security_monitor.py`: Main entry, frontend/backend integration, UI logic
- `security_monitor_backend.py`: Backend logic, ML/AI, integrity, plugins
- `security_monitor_backend_api.py`: Flask API server
- `system_monitor/monitor.py`: Minimal CLI monitor
- `SecurityBot/`: Enterprise orchestration, all major features as classes
- `tests/`: Pytest-based tests for backend/frontend
- `pyproject.toml`: Build, dependency, lint/type config

## Examples
- **Add a plugin**: Place a `.py` file with `get_metrics()` in `plugins/`; it will be auto-loaded.
- **Run with custom log file**: `python system_monitor/monitor.py --log-file mylog.txt`
- **Test ML/AI findings**: See `tests/test_security_monitor_backend.py` and `tests/test_security_monitor_frontend.py`
- **Verify SecurityBot deployment**: Run `python SecurityBot/deployment_verification_simple.py`

## Special Notes
- **Do not add strong-copyleft dependencies** (GPL/LGPL/AGPL) without approval.
- **Keep backend and frontend in sync** if changing API/data flows.
- **Document new endpoints or plugin interfaces** in this file for future agents.
