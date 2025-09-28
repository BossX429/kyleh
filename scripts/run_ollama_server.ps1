# PowerShell script to run the Ollama server
Set-Location -Path "$PSScriptRoot\..\ollama"
Start-Process -NoNewWindow -FilePath ".\ollama.exe" -ArgumentList "serve"
