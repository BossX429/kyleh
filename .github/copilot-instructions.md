---
# Copilot Coding Agent Onboarding: Security Monitor Repository

## Overview
This is a cross-platform, monolithic Python 3.8+ system security monitoring and optimization tool. It monitors CPU, RAM, GPU, disk, network, and processes for anomalies, privacy risks, and performance dips. The system supports ML/AI-based anomaly detection, self-healing, user automation, and plugin extensions. Optional Tkinter UI and REST API are provided for automation and testing.

## Architecture & Key Components
- **Backend** (`security_monitor_backend.py`): Core monitoring, ML/AI (IsolationForest, LinearRegression), plugin loading, integrity checks, user automation, and logging. Exposes a Flask API (`security_monitor_backend_api.py`).
- **Frontend/UI** (`security_monitor.py`): Tkinter-based UI, accessibility features, and integration with backend via HTTP. CLI-only mode via `system_monitor/monitor.py`.
- **Plugins**: Drop `.py` files with a `get_metrics()` function in a `plugins` directory; these are auto-loaded by the backend.
- **SecurityBot** (`SecurityBot/`): Advanced modules for alerting, reporting, threat detection, and automation.
- **Tests** (`tests/`): Pytest-based tests for backend and frontend.

## Developer Workflows
- **Install dependencies**:  
  - Normal: `python -m pip install .`  
  - Dev: `python -m pip install -e .[dev]`  
  - Use a virtual environment (`python -m venv .venv`)
- **Run**:  
  - UI+backend: `python security_monitor.py`  
  - CLI: `python system_monitor/monitor.py` (supports `--log-file`, `--interval`, etc.)  
  - REST API: `python security_monitor_backend_api.py`
- **Test**: `pytest` (see `tests/`)
- **Type check**: `mypy .` (strict)
- **Format**: `black .` and `isort .` (see `pyproject.toml`)

## Project Conventions & Patterns
- **Strict type checking**: Enforced via `mypy`/`pyright` (see `pyproject.toml`).
- **No lockfiles**: Do not use pip or npm lockfiles.
- **Logging**: All findings/metrics to `security_monitor.log` (configurable).
- **ML/AI**: Models retrained and saved as `ml_optimization_model.pkl`.
- **Self-healing**: Integrity checks and auto-restore/quarantine for monitored files (see `_integrity_*` methods).
- **User automation**: Configurable via user config (see `_load_user_automation`).
- **Accessibility**: UI supports high-contrast mode and font scaling (see `_apply_accessibility`).
- **Windows-specific**: WMI features if `wmi` is installed; some optimizations are Windows-only.
- **Dependencies**: All in `pyproject.toml` (see `[project]` and `[project.optional-dependencies]`).
- **No strong-copyleft dependencies** (GPL/LGPL/AGPL) without approval.

## Safety & File Protection (MANDATORY)
- **Never** hardlock, lock out, or delete system/OS/data files or user info. All destructive actions must have explicit, multi-level safeguards and user confirmation.
- All file operations must check paths and avoid any system, OS, or user data directories (e.g., `C:\Windows`, `/etc`, `/home`, `/Users`, or equivalents).
- Plugins, automation, and self-healing logic must never interfere with or modify system/OS files or critical user data.
- When creating or placing files, ensure they do not overwrite or conflict with existing files unless explicitly intended and safe. Use unique names and isolated directories where possible.
- All destructive or modifying actions must be logged and, where possible, reversible (e.g., quarantine instead of delete).
- If in doubt, default to non-destructive, reversible actions and require user/admin approval for any sensitive operation.

## Test & Validation Best Practices
- After any change, run `pytest` and verify all tests pass.
- Validate that new or modified files do not interfere with each other or with existing files—test in a clean environment if possible.
- Confirm that plugins, automation, and ML/AI features work as intended and do not cause side effects outside their intended scope.
- If adding new file types, directories, or automation, document their purpose and isolation strategy in this file.

## Additional Nuanced Patterns
- Plugins must have a `get_metrics()` function and reside in `plugins/`; backend auto-loads, no manual registration.
- ML/AI model paths/formats must not be hardcoded; use config and document changes.
- Extend `_integrity_*` methods if monitoring new files/resources.
- Update this file with any new API endpoints, plugin interfaces, or integration points.

## Integration Points
- **API**: Flask server exposes `/metrics`, `/findings`, `/optimize`, `/plugins`, `/automation`, `/state` endpoints.
- **Plugins**: Place `.py` files with `get_metrics()` in `plugins/` to extend monitoring.
- **Notifications**: Uses `plyer` (desktop) and `pyttsx3` (speech, optional).

## Examples
- **Add a plugin**: Place a `.py` file with `get_metrics()` in `plugins/`.
- **Run with custom log file**: `python system_monitor/monitor.py --log-file mylog.txt`
- **Test ML/AI findings**: See `tests/test_security_monitor_backend.py` and `tests/test_security_monitor_frontend.py`

## Key Files/Directories
- `security_monitor.py`: Main entry, UI/backend integration
- `security_monitor_backend.py`: Backend logic, ML/AI, plugins
- `security_monitor_backend_api.py`: Flask API server
- `system_monitor/monitor.py`: CLI monitor
- `SecurityBot/`: Advanced security modules
- `tests/`: Pytest-based tests
- `pyproject.toml`: Build, dependency, lint/type config

---
**If you update API endpoints, plugin interfaces, or add new integration points, document them here for future agents.**
