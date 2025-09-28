<#
Export local Ollama models to LOCAL_MODELS.md at the repository root.
Usage:
  .\export_local_models.ps1
#>

$hostUrl = 'http://localhost:11434'
$uri = "$hostUrl/api/tags"
$repoRoot = 'E:\A.I. Development'
$outFile = Join-Path $repoRoot 'LOCAL_MODELS.md'

try {
    Write-Host "Querying $uri" -ForegroundColor Cyan
    $res = Invoke-RestMethod -Uri $uri -Method Get -ErrorAction Stop
    if ($null -eq $res -or -not $res.models) {
        Write-Warning "No models returned from server. Is Ollama running?"
        exit 1
    }

    $md = "# Local models snapshot`n`nGenerated: $(Get-Date -Format o)`n`n"
    foreach ($m in $res.models) {
        $name = $m.name
        $sizeGB = [math]::Round(($m.size / 1GB), 2)
        $params = $m.details.parameter_size
        $format = $m.details.format
        $quant = $m.details.quantization_level
        $md += "- **$name** — $sizeGB GB, parameter_size: $params, format: $format, quantization: $quant`n"
    }

    Set-Content -Path $outFile -Value $md -Force -Encoding UTF8
    Write-Host "Wrote $outFile" -ForegroundColor Green
} catch {
    Write-Error "Failed to export local models: $_"
    exit 2
}
