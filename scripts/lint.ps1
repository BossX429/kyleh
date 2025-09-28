# Lint Go and JS code
if (Test-Path "..\ollama\") {
	Push-Location ..\ollama
	golangci-lint run
	Pop-Location
}
if (Test-Path "..\ollama\macapp\package.json") {
	Push-Location ..\ollama\macapp
	npx eslint .
	Pop-Location
}
