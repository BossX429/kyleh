# PowerShell script to check WSL installation and status
$wslStatus = wsl --status 2>&1

if ($wslStatus -match 'Default Distribution') {
    Write-Host "WSL is installed and ready!"
    wsl --list --verbose
} elseif ($wslStatus -match 'Windows Subsystem for Linux has no installed distributions') {
    Write-Host "WSL is installed, but no Linux distribution is set up. Run 'wsl --install' to complete setup."
} elseif ($wslStatus -match 'is not recognized') {
    Write-Host "WSL is not installed. Run 'wsl --install' in an administrator PowerShell."
} else {
    Write-Host "WSL status could not be determined. Output:"
    Write-Host $wslStatus
}
