# PowerShell script to run a default Ollama model
Set-Location -Path "$PSScriptRoot\..\ollama"
Start-Process -NoNewWindow -FilePath ".\ollama.exe" -ArgumentList "run llama3.2"
