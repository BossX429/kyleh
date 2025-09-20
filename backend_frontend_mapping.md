# Backend/frontend boundary mapping for SecurityMonitor refactor

## Backend (SecurityMonitorBackend)
- Core monitoring logic: _monitor_iteration, _check_cpu_usage, _check_ram_usage, _check_gpu_usage, _check_disk_io, _check_network_latency, _detect_performance_dips, _check_new_processes, _check_network_connections, _check_security_privacy, _check_fps_input_lag
- Optimization: _optimize_system, _close_background_apps, _boost_foreground_priority, _clear_ram_windows
- ML/AI: _ml_optimize, _load_ml_model
- Plugin system: _load_plugins, plugin management
- User automation: _run_user_automation, _run_user_action
- Integrity/self-healing: _init_integrity, _integrity_hash, _integrity_hash_all, _integrity_backup, _integrity_backup_all, _integrity_restore, _integrity_quarantine, _integrity_check, _start_integrity_thread
- Auto-update: _init_auto_update, _get_current_version, _check_for_update, _download_and_stage_update, _apply_staged_update, _start_update_thread
- Data: cpu_history, ram_history, gpu_history, disk_history, net_latency_history, net_jitter_history, privacy_findings, ml_data, plugins, user_automation, etc.
- API server: (to be implemented)

## Frontend (SecurityMonitorFrontend)
- UI: _setup_ui, _ui_log, _show_accessibility_options, _apply_accessibility, _show_privacy_dashboard
- Notifications: _notify
- Voice/TTS: _speak
- Accessibility: _init_accessibility, _load_accessibility_config, _save_accessibility_config
- Data fetch: fetches metrics, findings, etc. from backend API
- Actions: triggers optimization, automation, etc. via backend API

## Shared/Utility
- Logging: _setup_logging
- Signal handling: _signal_handler

## API Contract (initial proposal)
- GET /metrics: returns current CPU, RAM, GPU, disk, network stats
- GET /findings: returns recent privacy/security findings
- POST /optimize: triggers optimization
- GET /plugins: returns plugin/game telemetry
- GET /automation: returns automation status
- POST /automation/run: triggers user automation
- GET /state: returns system state (running, version, etc.)

This mapping will guide the refactor and API design.