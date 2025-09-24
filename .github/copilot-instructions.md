# Copilot Instructions for Security Monitor Codebase

## Architecture Overview
- **Monolithic Python app** with modular backend (`SecurityMonitorBackend`), frontend (`SecurityMonitorFrontend`), and legacy compatibility via `SecurityMonitor` class (see `security_monitor.py`).
- **Backend**: Handles system/resource monitoring, ML/AI anomaly detection, self-healing, plugin loading, and exposes a Flask API (`security_monitor_backend.py`, `security_monitor_backend_api.py`).
- **Frontend**: Optional Tkinter UI, notifications, accessibility, and privacy dashboards. Communicates with backend via HTTP (`security_monitor.py`).
- **Plugins**: Dynamically loaded from a `plugins` directory (see `_load_plugins` methods).
- **API**: Flask server exposes `/metrics`, `/findings`, `/optimize`, `/plugins`, `/automation`, `/state` endpoints for UI and automation.

## Developer Workflows
- **Install**: `python -m pip install .` (dev: `python -m pip install -e .[dev]`)
- **Run**: `python security_monitor.py` (UI+backend) or `python system_monitor/monitor.py` (CLI-only)
- **Test**: `pytest` (see `tests/`)
- **Format**: `black .` and `isort .` (see `pyproject.toml` for config)
- **Type check**: `mypy .` or use strict Pyright config
- **Dependencies**: Declared in `pyproject.toml` (see `[project]` and `[project.optional-dependencies]`)

## Project Conventions
- **Strict type checking**: Enforced via mypy/pyright (see `pyproject.toml`).
- **Logging**: All monitoring and findings are logged to `security_monitor.log` (configurable).
- **ML/AI**: Uses scikit-learn (IsolationForest, LinearRegression) for anomaly detection and optimization. Models are retrained periodically and persisted as `ml_optimization_model.pkl`.
- **Self-healing**: Integrity checks and auto-restore/quarantine for monitored files (see `_integrity_*` methods).
- **User automation**: Supports user-defined automation rules via config file (see `_load_user_automation`).
- **Accessibility**: UI supports high-contrast mode and font scaling (see `_apply_accessibility`).

## Integration Points
- **Flask API**: Used by frontend/UI and for automation/testing.
- **Plugins**: Drop Python files with a `get_metrics()` function in the plugins directory to extend monitoring.
- **Notifications**: Uses `plyer` for desktop notifications and `pyttsx3` for speech (optional).
- **Windows-specific**: WMI features enabled if `wmi` is installed; some optimizations are Windows-only.

## Key Files/Directories
- `security_monitor.py`: Main entry, frontend/backend integration, UI logic
- `security_monitor_backend.py`: Backend logic, ML/AI, integrity, plugins
- `security_monitor_backend_api.py`: Flask API server
- `system_monitor/monitor.py`: Minimal CLI monitor
- `tests/`: Pytest-based tests for backend/frontend
- `pyproject.toml`: Build, dependency, lint/type config

## Examples
- **Add a plugin**: Place a `.py` file with `get_metrics()` in the plugins dir; it will be auto-loaded.
- **Run with custom log file**: `python system_monitor/monitor.py --log-file mylog.txt`
- **Test ML/AI findings**: See `tests/test_security_monitor_backend.py` and `tests/test_security_monitor_frontend.py`

## Special Notes
- **Do not add strong-copyleft dependencies** (GPL/LGPL/AGPL) without approval.
- **Keep backend and frontend in sync** if changing API or data flows.
- **Document new endpoints or plugin interfaces** in this file for future agents.
