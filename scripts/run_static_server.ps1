<#
Run a simple static server for the demo repository.
Usage:
  # Node (recommended if you have Node):
  .\run_static_server.ps1 -Mode node

  # Python fallback:
  .\run_static_server.ps1 -Mode python
#>

param(
    [ValidateSet('node','python')]
    [string]$Mode = 'node'
)

$repoPath = 'E:\A.I. Development\Repos\demo-repository'
if (-not (Test-Path $repoPath)) {
    Write-Error "Demo repo not found at $repoPath"
    exit 1
}

Set-Location $repoPath
if ($Mode -eq 'node') {
    Write-Host "Installing dependencies (if missing) and running 'npx serve -s .'..." -ForegroundColor Cyan
    npm install | Out-Null
    npx serve -s .
} else {
    Write-Host "Starting Python HTTP server on port 8000..." -ForegroundColor Cyan
    python -m http.server 8000
}
