# Scheduled Tasks Examples

## Windows Task Scheduler
- Use `scripts/install_ollama_autostart.ps1` for auto-start.
- Use Task Scheduler to run `scripts/update_models.ps1` or `scripts/backup.ps1` daily.

## Linux (cron)
```
@reboot /path/to/ollama/ollama serve
0 2 * * * /path/to/ollama/ollama pull llama3.2
0 3 * * * /path/to/backup.sh
```

## macOS (launchd)
- Create a `~/Library/LaunchAgents/ollama.server.plist` to auto-start the server.
