# PowerShell script to build the Ollama binary
Set-Location -Path "$PSScriptRoot\..\ollama"
go build .
