<#
List local Ollama models via HTTP API and pretty-print JSON.
Usage: Open PowerShell and run:
  .\list_models.ps1
#>

$hostUrl = 'http://localhost:11434'
$uri = "$hostUrl/api/tags"
try {
    Write-Host "Requesting model list from $uri" -ForegroundColor Cyan
    $res = Invoke-RestMethod -Uri $uri -Method Get -ErrorAction Stop
    if ($null -eq $res) {
        Write-Warning "No response from server. Is Ollama running?"
        exit 1
    }
    $res | ConvertTo-Json -Depth 6
} catch {
    Write-Error "Failed to list models: $_"
    Write-Host "Try: Start the Ollama server (e.g. .\\ollama.exe serve) and re-run this script." -ForegroundColor Yellow
    exit 2
}
