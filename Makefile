# Cross-platform Makefile for Ollama automation

.PHONY: all build run serve test desktop install-windows-autostart

all: build

build:
	go build .

serve:
	./ollama serve

run:
	./ollama run llama3.2

test:
	go test -tags=integration ./...

desktop:
	cd macapp && npm install && npm start

install-windows-autostart:
	powershell -ExecutionPolicy Bypass -File scripts\install_ollama_autostart.ps1
