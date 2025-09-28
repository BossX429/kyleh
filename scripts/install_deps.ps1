# Install Go, Node, and Python dependencies
# Go dependencies
if (Test-Path "..\ollama\go.mod") {
	Push-Location ..\ollama
	go mod tidy
	Pop-Location
}
# Node dependencies
if (Test-Path "..\ollama\macapp\package.json") {
	Push-Location ..\ollama\macapp
	npm install
	Pop-Location
}
# Python dependencies (if any requirements.txt)
if (Test-Path "..\ollama\requirements.txt") {
	Push-Location ..\ollama
	pip install -r requirements.txt
	Pop-Location
}
