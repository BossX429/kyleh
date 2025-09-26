---
# Copilot Coding Agent Onboarding: Security Monitor Repository

## Repository Summary
- **Purpose:** Python-based system security monitoring and optimization tool. Monitors CPU, RAM, GPU, disk, network, and processes for anomalies, privacy risks, and performance dips. Supports ML/AI-based anomaly detection, self-healing, user automation, and plugin extensions. Optional Tkinter UI frontend and REST API for automation/testing.
- **Type:** Monolithic Python project (Python 3.8+), cross-platform (Windows features enhanced), with modular backend, frontend, and plugin system.
- **Size:** Medium (dozens of source files, multiple submodules, tests, and scripts).
- **Languages/Frameworks:** Python 3.8+, Flask (API), Tkinter (UI), scikit-learn (ML), psutil, plyer, pyttsx3, pytest, black, isort, mypy, pyright.

## Build, Test, and Validation Instructions

### Environment Setup
- **Python version:** 3.8+ (recommend 3.8–3.10 for best compatibility)
- **Install dependencies:**
  - For normal use: `python -m pip install .`
  - For development: `python -m pip install -e .[dev]`
  - Always use the above commands before running, building, or testing.
- **Virtual environment:** Strongly recommended. Example:
  - `python -m venv .venv`
  - On Windows: `./.venv/Scripts/Activate.ps1`
  - On Unix: `source .venv/bin/activate`

### Build/Run
- **Run with UI and backend:** `python security_monitor.py`
- **Run CLI-only:** `python system_monitor/monitor.py` (supports `--log-file`, `--interval`, etc.)
- **Run REST API only:** `python security_monitor_backend_api.py` (if present)

### Test
- **Run all tests:** `pytest` (tests in `tests/`)
- **Test files:** `tests/test_security_monitor_backend.py`, `tests/test_security_monitor_frontend.py`
- **Type check:** `mypy .` (strict, see `pyproject.toml`)
- **Lint/format:** `black .` and `isort .` (see config in `pyproject.toml`)

### Validation/CI
- **Pre-checkin:** Always run `pytest`, `mypy .`, `black .`, and `isort .` before submitting changes.
- **No lockfile:** Do not use pip or npm lockfiles; always install as above.
- **Known issues:**
  - Some features require optional dependencies (`wmi` for Windows, `plyer`, `pyttsx3`, `GPUtil`, `tkinter`).
  - If a dependency is missing, the app will warn and disable the feature, but will not crash.
  - If you see type errors, check that you are using Python 3.8+ and have all dev dependencies installed.

## Project Layout and Architecture

- **Root files:**
  - `security_monitor.py`: Main entry, frontend/backend integration, UI logic
  - `security_monitor_backend.py`: Backend logic, ML/AI, integrity, plugins
  - `security_monitor_backend_api.py`: Flask API server
  - `system_monitor/monitor.py`: Minimal CLI monitor
  - `pyproject.toml`: Build, dependency, lint/type config
  - `setup.ps1`: Windows setup script
  - `README.md`: Usage and install instructions
- **Directories:**
  - `system_monitor/`: Core CLI monitor and versioning
  - `SecurityBot/`: (Advanced) Security bot modules (alerting, reporting, threat detection, etc.)
  - `tests/`: Pytest-based tests for backend/frontend
  - `Development/`: Dev scripts, configs, and Copilot enhancer tools
- **Plugins:** Place `.py` files with a `get_metrics()` function in a `plugins` directory (auto-loaded by backend).
- **API:** Flask server exposes `/metrics`, `/findings`, `/optimize`, `/plugins`, `/automation`, `/state` endpoints for UI and automation.
- **Logging:** All monitoring and findings are logged to `security_monitor.log` (configurable via CLI/UI).
- **ML/AI:** Uses scikit-learn (IsolationForest, LinearRegression) for anomaly detection and optimization. Models are retrained and saved as `ml_optimization_model.pkl`.
- **Self-healing:** Integrity checks and auto-restore/quarantine for monitored files (see `_integrity_*` methods).
- **User automation:** Supports user-defined automation rules via config file (see `_load_user_automation`).
- **Accessibility:** UI supports high-contrast mode and font scaling (see `_apply_accessibility`).

## Key Validation Steps
- Always run `python -m pip install -e .[dev]` before running tests or type checks.
- Always run `pytest` and `mypy .` before submitting changes.
- Always run `black .` and `isort .` to auto-format code.
- If adding dependencies, update `pyproject.toml` and ensure no strong-copyleft licenses are introduced.
- If changing API or data flows, keep backend and frontend in sync.

## Trust These Instructions
- Trust these instructions for build, test, and run steps. Only search the codebase if information here is incomplete or found to be in error.

---# Copilot Instructions for Security Monitor Codebase

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

## .NET CLI Telemetry Notice

The .NET tools collect usage data to help improve your experience. This data is collected by Microsoft and shared with the community. You can opt out of telemetry by setting the `DOTNET_CLI_TELEMETRY_OPTOUT` environment variable to `1` or `true` in your shell.

Read more: https://aka.ms/dotnet-cli-telemetry

# Spellchecker dictionary additions for cSpell
# Add the following words to your cSpell user or workspace dictionary to avoid false positives:
# Tkinter, scikit, psutil, plyer, pyttsx3, pytest, isort, mypy, pyright, venv, pyproject, checkin, lockfiles, OPTOUT, mylog, Pytest
#
# To add these words, create or update a `.cspell.json` file in the repo root with:
#
# {
#   "version": "0.2",
#   "words": [
#     "Tkinter", "scikit", "psutil", "plyer", "pyttsx3", "pytest", "isort", "mypy", "pyright", "venv", "pyproject", "checkin", "lockfiles", "OPTOUT", "mylog", "Pytest"
#   ]
# }
#
# This will silence cSpell warnings for these technical/project-specific terms.
