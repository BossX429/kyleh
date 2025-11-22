## User/Agent Feedback Loop

To continuously improve features and workflows:

- **Feedback Collection:**
  - Provide a feedback endpoint (e.g., `/feedback` in REST API) or accept feedback via config file or issue tracker.
  - Example feedback stub:
    ```python
    # feedback.py
    def submit_feedback(user, message):
        with open('feedback.log', 'a') as f:
            f.write(f"{user}: {message}\n")
    ```
- **Review Process:**
  - Regularly review feedback logs or issues.
  - Prioritize actionable items using the quad sequence formula.
  - Document changes and responses in onboarding or changelog.
## Disaster Recovery & Audit Guide

To ensure resilience and recoverability:

- **Backup:** Regularly back up configs, models, and critical data to a safe location.
- **Restore:** Test restore procedures periodically; use integrity/self-healing features for automated recovery.
- **Audit:** Log all destructive or modifying actions, config changes, and rollbacks for traceability.
- **Test Scenarios:**
  - Simulate data loss or corruption and verify full recovery.
  - Test rollback of configs, models, and plugins.
  - Review audit logs for completeness and accuracy.
## Plugin & Automation Registry Concept

To encourage sharing and review of plugins and automation scripts:

- **Registry Structure:**
  - Use a shared directory or repository (e.g., `plugins/registry/` or a dedicated GitHub repo).
  - Each plugin/automation script should include a manifest with name, version, author, description, and compatibility info.
- **Contribution Guidelines:**
  - Submit new plugins/scripts via pull request or registry submission process.
  - All contributions must include tests and documentation.
  - Reviewers check for safety, compatibility, and code quality before merging.
- **Review & Update Process:**
  - Periodically review registry for outdated or vulnerable plugins/scripts.
  - Deprecate or update as needed; notify users of breaking changes.
## ML/AI Model Monitoring & Retraining

To maintain high model performance and reliability:

- **Monitor Model Performance:** Log model accuracy, drift, and prediction errors over time.
- **Alerting:** Set up alerts for significant drops in model performance or data drift.
- **Retraining Workflow:**
  - Periodically retrain models with new data.
  - Validate retrained models before deployment.
  - Roll back to previous models if new ones underperform.
- **Example Monitoring Stub:**
  ```python
  # ml_monitoring.py
  def log_model_metrics(metrics):
      with open('ml_metrics.log', 'a') as f:
          f.write(str(metrics) + '\n')
  def check_drift(current_metrics, baseline):
      # Compare and alert if drift exceeds threshold
      pass
  ```
- **Best Practices:**
  - Automate model evaluation and retraining in CI/CD where possible.
  - Store all model versions and metrics for audit and rollback.
## Configuration Management & Rollback

To ensure safe and reliable configuration changes:

- **Validation:** Always validate config files (e.g., with `python -m json.tool` for JSON) before applying changes.
- **Drift Detection:** Periodically compare current configs to version-controlled or golden configs to detect drift.
- **Rollback:**
  - Keep backups of previous config versions before applying changes.
  - Use integrity/self-healing features to restore known-good configs if issues are detected.
  - Document all config changes and rollbacks in logs for auditability.
- **Best Practices:**
  - Store configs in version control where possible.
  - Automate config validation and backup in deployment scripts.
  - Test config changes in a staging environment before production.
## Deployment Verification in CI/CD

Integrate deployment verification to ensure all components work after deployment:

- **Script:** Use `SecurityBot/deployment_verification.py` to test modules, database, UI, and dashboard.
- **Workflow Integration:** Add a step in your GitHub Actions workflow:
  ```yaml
  - name: Run deployment verification
    run: |
      python SecurityBot/deployment_verification.py
  ```
- **Best Practices:**
  - Run after main tests and before production deployment.
  - Review logs for failures and address any issues before release.
  - Update verification script as new features are added.
## Automated UI/UX Testing

To ensure UI/UX quality and prevent regressions, implement automated UI/UX tests:

- **Recommended Tools:**
  - [Selenium](https://www.selenium.dev/) for browser-based dashboard testing.
  - [PyAutoGUI](https://pyautogui.readthedocs.io/) for desktop UI automation.
  - [pytest](https://docs.pytest.org/) for test orchestration.

- **Example Selenium Test Stub:**
  ```python
  # tests/test_dashboard_ui.py
  from selenium import webdriver
  def test_dashboard_loads():
      driver = webdriver.Chrome()
      driver.get('http://localhost:8080')
      assert 'Security Dashboard' in driver.title
      driver.quit()
  ```

- **Example PyAutoGUI Test Stub:**
  ```python
  # tests/test_desktop_ui.py
  import pyautogui
  def test_ui_button():
      button = pyautogui.locateOnScreen('button.png')
      assert button is not None
      pyautogui.click(button)
  ```

- **Integration Guidance:**
  - Add UI/UX tests to the `tests/` directory.
  - Run UI/UX tests in CI/CD where possible (use headless mode for Selenium).
  - Document any manual steps or screenshots required for visual validation.
  - Ensure accessibility features (font scaling, high-contrast) are covered by tests.
## Agent Speed & Responsiveness Optimization

To maximize the speed and responsiveness of Copilot agents and automation:

- **Minimize File Reads:** Use semantic and targeted searches instead of reading large files line-by-line. Prefer summary tools and indexed lookups.
- **Cache Results:** Cache expensive or repeated queries (e.g., API schema, config structure) during a session.
- **Batch Operations:** Where possible, batch file edits, test runs, or validation steps to reduce round-trips.
- **Parallelize Tasks:** Use parallel tool invocations for independent actions (e.g., searching, linting, or test discovery).
- **Preload Context:** Preload key onboarding, config, and workflow files at session start for instant access.
- **Optimize Search Patterns:** Use precise, high-signal search queries and avoid broad, slow scans.
- **Automate Routine Checks:** Script and automate repetitive validation (e.g., config validation, test runs) to avoid manual delays.
- **Profile and Monitor:** Regularly profile agent operations and monitor for slow steps; optimize or refactor as needed.
- **Document Fast Paths:** Clearly document the fastest onboarding, troubleshooting, and upgrade paths for new agents and contributors.

**Example Fast Onboarding Flow:**
1. Preload `.github/copilot-instructions.md`, `pyproject.toml`, and key config files.
2. Use semantic search to locate integration points and extension hooks.
3. Batch validate config and run all tests in parallel.
4. Use cached API and plugin schemas for code generation.
5. Document and share any new speed optimizations in this file.
## Continuous Improvement: Quad Sequence Formula

To ensure ongoing upgrades, improvements, and project excellence, use the following Quad Sequence Formula for any feature, workflow, or integration point:

**1. Observe**
- Collect data, logs, and user feedback on the current feature or process.
- Identify pain points, bottlenecks, or areas of ambiguity.

**2. Analyze**
- Cross-reference observations with project goals, safety rules, and best practices.
- Compare with similar open-source projects or industry standards.
- Document gaps, risks, and opportunities for enhancement.

**3. Prototype**
- Design and implement a minimal, reversible upgrade or improvement.
- Ensure all changes are covered by tests and documented in this file.
- Solicit feedback from users, agents, or maintainers.

**4. Integrate**
- Merge successful prototypes into the main workflow or codebase.
- Update onboarding, documentation, and safety checklists.
- Monitor for regressions or new issues; repeat the cycle as needed.

**Usage Example:**
- When adding a new plugin type, first observe how current plugins are used, analyze gaps, prototype a new interface, and integrate after validation.
- For deployment upgrades, observe CI/CD logs, analyze failures, prototype a new workflow step, and integrate if it improves reliability.

**This formula should be applied to all new features, refactors, and process changes to ensure continuous improvement and project resilience.**
## MCP Server Configuration Fields

| Field      | Description                                 | Required | Example                      |
|------------|---------------------------------------------|----------|------------------------------|
| name       | Human-readable name for display in UI       | Yes      | "Filesystem Indexer"         |
| id         | Unique identifier for the server            | Yes      | "file-system"                |
| transport  | Connection protocol and parameters          | Yes      | { "type": "stdio", ... }     |

### Technical Details and Advanced Features
- **Automatic Discovery:** The extension parses the `mcpServers` config, establishes connections, and queries each server for available tools automatically at startup or config reload.
- **Extensible Transport Layer:** Supports multiple transport mechanisms (stdio, SSE) and is designed for future protocols without core changes.
- **Seamless Integration:** MCP-enabled tools appear and function like native tools in the UI. The AI can invoke them autonomously as needed.
- **Deployment Flexibility:** Supports local processes, Docker containers, and remote HTTP services for flexible deployment.

### Supported Deployment Models
- **Local Processes:** Run directly on your machine using stdio transport.
- **Docker Containers:** Isolated, consistent execution environments.
- **Remote Services:** Connect to HTTP endpoints via SSE transport.
---
# Copilot Coding Agent Onboarding: Security Monitor Repository

> **Note:** Tools are automatically detected and made available in the sidebar with real-time status.

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
**MCP server extensibility**: Add new MCP servers by updating configuration—no code changes required. The configuration is JSON-based and supports multiple servers with stdio and SSE transport protocols. Document config changes here if integration points or patterns change.

### Example MCP Server Configuration
```json
{
  "mcpServers": {
    "your-server-id": {
      "name": "Server Name",
      "id": "your-server-id",
      "transport": {
        "type": "stdio|sse",
        // For stdio transport:
        "command": "npx|docker|node",
        "args": ["-y", "package-name", "--optional-flag"],
        "env": {
          "API_KEY": "your_api_key"
        }
        // For SSE transport:
        // "url": "https://your-server.com/sse"
      },
      "enabled": true
    }
  }
}
```


## API Reference
| Method | Path                | Description                                 |
|--------|---------------------|---------------------------------------------|
| GET    | /metrics            | Returns current CPU, RAM, GPU, disk, network stats |
| GET    | /findings           | Returns recent privacy/security findings     |
| POST   | /optimize           | Triggers optimization                       |
| GET    | /plugins            | Returns plugin/game telemetry               |
| GET    | /automation         | Returns automation status                   |
| POST   | /automation/run     | Triggers user automation                    |
| GET    | /state              | Returns system state (running, version, etc)|

## Plugin Authoring Guide
- Place `.py` files with a `get_metrics()` function in `plugins/`.
- `get_metrics()` should return a dict with plugin name, metrics, and status. Example:
  ```python
  def get_metrics():
      return {"name": "example_plugin", "metrics": {"fps": 60}, "status": "ok"}
  ```
- Plugins must not modify or delete system/user files. Log all actions.
- Test plugins in isolation before deployment.

## User Automation Config
- Place a JSON file with automation rules. Example:
  ```json
  {
    "triggers": [
      {"app": "game.exe", "action": "optimize", "on": "start"},
      {"app": "browser.exe", "action": "reduce_priority", "on": "focus"}
    ]
  }
  ```
- Supported actions: optimize, reduce_priority, notify, etc.
- Validate config with `python -m json.tool` before use.

## Self-Healing & Integrity
- Integrity checks run every 60s; see `_integrity_check` and related methods.
- To extend: add new file types or directories to monitor in `_integrity_check`.
- All destructive actions must be reversible (quarantine, restore).
- Log all integrity events for audit.

## Deployment & CI/CD
- Use `SecurityBot/deploy.py` for deployment automation and checks.
- Prerequisites: Python 3.8+, required modules (see deploy.py), Windows OS.
- Run post-deployment tests automatically.
- Rollback: Use backup/restore features in integrity system.
- Example GitHub Actions workflow:
  ```yaml
  on: [push, pull_request, workflow_dispatch]
  jobs:
    test:
      runs-on: windows-latest
      steps:
        - uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.8'
        - name: Install dependencies
          run: python -m pip install -e .[dev]
        - name: Run tests
          run: pytest
  ```

## Testing & Validation
- All new features must include tests in `tests/`.
- Example: To test a plugin, add `test_plugin_example.py`.
- Run `pytest` after any change; all tests must pass.
- Use `mypy .` for type checking.

## Accessibility & UI/UX
- UI supports high-contrast mode and font scaling.
- Customize via `accessibility_config.json`. Example:
  ```json
  {"font_size": 14, "high_contrast": true}
  ```
- Test accessibility features before release.

## Advanced Extensibility
- To add a new MCP server: update `mcp.json` as documented above.
- To add new REST API endpoints: document in this file and update API Reference.
- To add new plugin types: document interface and test coverage here.

## Security & Safety Checklist
- [ ] No plugin or automation modifies/deletes system/user files without explicit, logged, and reversible action.
- [ ] All file operations avoid system/OS/user data directories.
- [ ] All destructive actions are logged and reversible.
- [ ] All new endpoints, plugins, and automation are documented here.
- [ ] All new code is covered by tests and type checks.

----
**If you update API endpoints, plugin interfaces, or add new integration points, document them here for future agents.**
