<#
Helper to run Codacy CLI analysis for a file or the whole repo.
This wrapper attempts to call the Codacy MCP analyze tool locally if installed. If Codacy CLI is not available, it prints instructions.

Usage:
  .\codacy_check.ps1 -FilePath '.\\.github\\copilot-instructions.md'
  .\codacy_check.ps1  # analyze whole repo
#>

param(
    [string]$FilePath = '',
    [string]$RootPath = 'E:\A.I. Development'
)

function Show-Help {
    Write-Host "Codacy CLI wrapper" -ForegroundColor Cyan
    Write-Host "";
    Write-Host "Codacy CLI not found on PATH. Choose one of the options below to run analysis:" -ForegroundColor Yellow
    Write-Host "";
    Write-Host "1) Install Codacy CLI (manual download)" -ForegroundColor Green
    Write-Host "   - Open: https://github.com/codacy/codacy-analysis-cli/releases" -ForegroundColor White
    Write-Host "   - Download the latest windows zip, extract, and add the folder containing 'codacy.exe' to your PATH." -ForegroundColor White
    Write-Host "   - Example (PowerShell):" -ForegroundColor White
    Write-Host "     Invoke-WebRequest -Uri '<release-zip-url>' -OutFile C:\temp\codacy.zip" -ForegroundColor Gray
    Write-Host "     Expand-Archive C:\temp\codacy.zip -DestinationPath C:\tools\\codacy" -ForegroundColor Gray
    Write-Host "     [Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';C:\tools\\codacy', [EnvironmentVariableTarget]::User)" -ForegroundColor Gray
    Write-Host "";
    Write-Host "2) Use Docker (no install)" -ForegroundColor Green
    Write-Host "   - If you have Docker, run the analyzer via the official image:" -ForegroundColor White
    Write-Host "     docker run --rm -v ${PWD}:/src codacy/codacy-analysis-cli analyze --path /src/.github/copilot-instructions.md" -ForegroundColor Gray
    Write-Host "";
    Write-Host "3) Use the MCP / Codacy MCP server (if configured)" -ForegroundColor Green
    Write-Host "   - Ensure WSL is available and MCP tools are configured for your environment before retrying the MCP invocation." -ForegroundColor White
    Write-Host "";
    Write-Host "If you're unsure, try option 2 (Docker) for a fast, dependency-free run." -ForegroundColor Yellow
}

# Try to find a local codacy CLI (best-effort) under a few common names
$codacyCmd = Get-Command codacy -ErrorAction SilentlyContinue;
if (-not $codacyCmd) { $codacyCmd = Get-Command codacy-cli -ErrorAction SilentlyContinue }
if (-not $codacyCmd) { $codacyCmd = Get-Command codacy-analysis-cli -ErrorAction SilentlyContinue }

if (-not $codacyCmd) {
    Show-Help
    exit 2
}

try {
    if ([string]::IsNullOrEmpty($FilePath)) {
        Write-Host "Running codacy analyze on root: $RootPath" -ForegroundColor Cyan
        & $codacyCmd.Source analyze --path $RootPath
    } else {
        Write-Host "Running codacy analyze on: $FilePath" -ForegroundColor Cyan
        & $codacyCmd.Source analyze --path $FilePath
    }
} catch {
    Write-Error "Codacy analyze failed: $_"
    Show-Help
    exit 3
}
