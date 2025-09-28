# Example: trigger build from Slack/Discord webhook
param([string]$event)
if ($event -eq 'build') {
    # Trigger build pipeline, e.g., via GitHub Actions API or local script
    Write-Host 'Build triggered by chat!'
}
