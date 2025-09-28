# PowerShell script to install Visual Studio Build Tools with C++ workload
# Run as Administrator

$ErrorActionPreference = 'Stop'

# Download Visual Studio Build Tools bootstrapper
$vsInstallerUrl = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
$vsInstallerPath = "$env:TEMP\vs_BuildTools.exe"

if (!(Test-Path $vsInstallerPath)) {
    Invoke-WebRequest -Uri $vsInstallerUrl -OutFile $vsInstallerPath
}

# Install required C++ build tools silently
Start-Process -FilePath $vsInstallerPath -ArgumentList `
    "--quiet --wait --norestart --nocache --installPath C:\BuildTools `
    --add Microsoft.VisualStudio.Workload.VCTools `
    --add Microsoft.VisualStudio.Component.Windows10SDK.19041 `
    --add Microsoft.VisualStudio.Component.VC.CMake.Project `
    --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 `
    --add Microsoft.VisualStudio.Component.VC.CoreBuildTools `
    --add Microsoft.VisualStudio.Component.VC.ATL `
    --add Microsoft.VisualStudio.Component.VC.Llvm.Clang `
    --add Microsoft.VisualStudio.Component.VC.Llvm.ClangToolset `
    --add Microsoft.VisualStudio.Component.VC.CLI.Support `
    --add Microsoft.VisualStudio.Component.VC.Redist.14.Latest `
    --add Microsoft.VisualStudio.Component.Windows11SDK.22000 `
    --includeRecommended --includeOptional" `
    -Verb RunAs -Wait

Write-Host "Visual Studio Build Tools with C++ workload installation complete. Please restart your terminal or computer if prompted."
