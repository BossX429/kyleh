# Run Go benchmarks
if (Test-Path "..\ollama\") {
    Push-Location ..\ollama
    go test -bench=. ./...
    Pop-Location
}
