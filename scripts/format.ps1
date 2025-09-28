# Format Go and JS code
if (Test-Path "..\ollama\") {
	Push-Location ..\ollama
	go fmt ./...
	Pop-Location
}
if (Test-Path "..\ollama\macapp\package.json") {
	Push-Location ..\ollama\macapp
	npx prettier --write .
	Pop-Location
}
