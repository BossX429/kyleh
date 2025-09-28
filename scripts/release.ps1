# Automated release script
param([string]$version)
if (-not $version) { Write-Host 'Usage: .\release.ps1 <version>'; exit 1 }
git tag $version
git push origin $version
# Update changelog, build artifacts, etc. as needed
