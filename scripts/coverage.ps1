# Generate and upload test coverage (Codecov example)
if (Test-Path "..\ollama\") {
    Push-Location ..\ollama
    go test -coverprofile=coverage.out ./...
    # Upload to Codecov (requires CODECOV_TOKEN env var)
    if ($env:CODECOV_TOKEN) {
        Invoke-WebRequest -Uri "https://codecov.io/bash" -OutFile "codecov.sh"
        bash codecov.sh -t $env:CODECOV_TOKEN
    }
    Pop-Location
}
