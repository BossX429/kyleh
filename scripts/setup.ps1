# One-click environment setup
# Clone repo, install dependencies, build, configure auto-start
# (Assume repo already cloned)
& "$PSScriptRoot\install_deps.ps1"
& "$PSScriptRoot\build_ollama.ps1"
& "$PSScriptRoot\install_ollama_autostart.ps1"
