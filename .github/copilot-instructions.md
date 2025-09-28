# Copilot & AI Agent Instructions for the Ollama Codebase

## Project Overview
- **Ollama** enables running, customizing, and serving large language models locally, with a focus on developer extensibility and cross-platform support (macOS, Windows, Linux, Docker).
- The architecture is modular: core server, desktop app, API, model runners, and integration with [llama.cpp](https://github.com/ggerganov/llama.cpp) via Go bindings.

## Key Components & Structure
- `README.md` (root): Quickstart, CLI, REST API, and model library usage.
- `runner/`: Minimal HTTP server for model inference (`runner -model <model binary>`).
- `integration/`: Integration tests (run with `go test -tags=integration ./...`).
- `docs/`: Developer, API, and platform-specific documentation.
- `api/examples/`: Go code samples for API usage.
- `macapp/`, `app/`: Desktop app (build with `npm start` after building `ollama` binary).
- `llama/`: Go bindings and vendoring for `llama.cpp` and `ggml` (see `Makefile.sync`).

## Developer Workflows
- **Build core binary:** `go build .` (from repo root)
- **Run server:** `./ollama serve`
- **Run a model:** `./ollama run <model>`
- **Desktop app (macOS):** Build Go binary, then `npm install && npm start` in `macapp/`
- **Windows installer:** Run `powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1`
- **Integration tests:** `go test -tags=integration ./...` (see `integration/README.md` for tag options)
- **Vendoring llama.cpp:** Use `make -f Makefile.sync apply-patches` and follow `llama/README.md` for patch/merge workflow.

## Project-Specific Conventions
- **Model customization:** Use `Modelfile` with `FROM` and `PARAMETER` instructions, then `ollama create <name> -f Modelfile`.
- **REST API:** Exposed at `localhost:11434` (see `docs/api.md`).
- **Model management:** Use `ollama pull`, `ollama rm`, `ollama cp`, `ollama list`, `ollama ps`, `ollama stop`.
- **Integration tests** default to a small model, override with `OLLAMA_TEST_DEFAULT_MODEL`.
- **Test against running server:** Set `OLLAMA_TEST_EXISTING` and `OLLAMA_HOST` env vars.

## External Integrations
- **llama.cpp**: Vendored in `llama/`, patched via `Makefile.sync`.
- **Community UIs, libraries, and plugins:** See root `README.md` for extensive list and links.

## Examples
- Run a model: `ollama run llama3.2`
- REST API call: `curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "prompt":"Why is the sky blue?"}'`
- Customize a model: see `Modelfile` and `README.md`.

## References
- For platform-specific build/run, see `docs/`.
- For API usage, see `docs/api.md` and `api/examples/`.
- For vendoring/patching, see `llama/README.md`.

---

**Update this file as workflows or conventions evolve.**

{
  "editor.formatOnSave": true,
  "files.autoSave": "afterDelay",
  "editor.tabSize": 4,
  "editor.renderWhitespace": "all"
}
