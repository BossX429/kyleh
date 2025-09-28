# Generate documentation (Go example)
if (Test-Path "..\ollama\") {
    Push-Location ..\ollama
    godoc -http=:6060
    Pop-Location
}
