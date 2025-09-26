# Ensure logs directory + log file
$logDir = Join-Path $PSScriptRoot "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

$runLog = Join-Path $logDir "journal-run.log"