

# Copilot & AI Agent Instructions – Unified Workspace Guide

## Workspace Overview
This workspace contains two major projects:
- **Ollama**: Modular LLM server, desktop app, API, model runners, Go/JS/Python integrations, and developer docs.
- **demo-repository**: HTML/JS demo site with strict workflow automation, CI/CD, and onboarding for new contributors.

All automation, linting, formatting, pre-commit, CI, and security checks are enabled by default. All agents and contributors must follow these rules for every file and workflow.

---

## Getting Started (Checklist)
1. **Clone the repository** and open in VS Code.
2. **Install dependencies**:
	 - For Ollama: Ensure Go is installed, then run `go build .` in the root.
	 - For demo-repository: Run `npm install` in `Repos/demo-repository/`.
3. **Run lint and pre-commit checks** before pushing any changes.
4. **Review key files**: `README.md`, `PLAYBOOK.md`, `JOURNEY_LOG.md`, `.github/workflows/`.
5. **Ask Copilot** for workflow or codebase guidance as needed.

---
## Ollama: Key Workflows & Structure
- **Build core binary:** `go build .` (from repo root)
**Key Directories & Files:**
- `README.md` (root): Quickstart, CLI, REST API, and model library usage
---
## demo-repository: Key Workflows & Structure
**Examples:**
- **Run a model:**
	```sh
	./ollama run llama3.2
	```
- **Sample REST API call:**
	```sh
	curl http://localhost:11434/api/generate -d '{"model": "llama3.2", "prompt": "Why is the sky blue?"}'
	```
- **Model customization (Modelfile):**
	```Dockerfile
	FROM llama3.2
	PARAMETER temperature 0.7
	PARAMETER num_predict 128
	```
	Then run:
	```sh
	ollama create my-custom-model -f Modelfile
	```

---

## Cross-Project Integration
- The **demo-repository** can be used to build web UIs or demos that interact with Ollama’s REST API (localhost:11434).
- Example: Add JavaScript in `demo-repository/index.html` to POST to `http://localhost:11434/api/generate` and display model output.
- For advanced integration, see `docs/api.md` in Ollama and reference the API from the demo site.

---

## API contract (summary)
This workspace uses Ollama's HTTP API (see `ollama/docs/api.md`). Key points for clients and agents:

- Endpoint: `POST /api/generate` (streaming by default). Set `{"stream": false}` to receive a single JSON object.
- Minimum request shape:

```json
{ "model": "llama3.2", "prompt": "<your prompt>", "stream": false }
```

- Advanced fields: `options` (model params like `temperature`, `num_predict`), `format` (for JSON/schema outputs), `images` (base64 list), `raw`, `keep_alive`.
- Streaming response: a sequence of JSON objects. Final object contains `done: true` and statistics (`total_duration`, `eval_count`, etc.).
- Example final (non-streaming) response:

```json
{
	"model": "llama3.2",
	"created_at": "...",
	"response": "The sky is blue because...",
	"done": true,
	"total_duration": 5043500667
}
```

Note: some clients may prefer `stream: false` to simplify parsing. If you need streaming behaviour (e.g., for incremental UI updates), use a streaming-aware client.

---

## Windows / PowerShell quick commands
Use these copy/paste commands on Windows (PowerShell) when working locally.

- Build (Ollama Go binary):

```powershell
cd 'E:\A.I. Development\ollama'
go build .
```

- Run server (PowerShell):

```powershell
.\ollama.exe serve
# or from WSL: ./ollama serve
```

- Run a model locally (PowerShell):

```powershell
.\ollama.exe run llama3.2
```

- Set env vars for tests (PowerShell):

```powershell
$env:OLLAMA_TEST_EXISTING = '1'
$env:OLLAMA_HOST = 'http://localhost:11434'
```

---

## Try it: end-to-end (quick walkthrough)
This reproduces a simple end-to-end flow (run server, query from demo site):

1. Build and start the server (in a terminal):

```powershell
cd 'E:\A.I. Development\ollama'
go build .
.\ollama.exe serve
```

2. Option A — Non-streaming test with curl (single JSON response):

```powershell
curl http://localhost:11434/api/generate -H 'Content-Type: application/json' -d '{"model":"llama3.2","prompt":"Why is the sky blue?","stream":false}'
```

3. Option B — Quick demo page (open `Repos/demo-repository/index.html` in a browser or run a local static server) and paste the example HTML/JS below.

4. If something fails: check server logs in the terminal running `ollama serve`, confirm port 11434 is free, and verify the model name is available via `curl http://localhost:11434/api/tags`.


## Local models (list, run, pull/create)

This workspace expects contributors to be able to list and run local models using the Ollama CLI or the HTTP API. Use these quick commands to see what models are available locally, run a model interactively, or add/pull models.

Listing models (curl):

```powershell
# PowerShell (returns JSON array of tag objects)
Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -Method Get | ConvertTo-Json -Depth 4

# curl (raw output)
curl http://localhost:11434/api/tags
```

Listing models (Ollama CLI):

```powershell
cd 'E:\A.I. Development\ollama'
.
# If using the built binary (Windows)
.\ollama.exe tags
# or from WSL / Unix:
./ollama tags
```

Run a model locally (interactive):

```powershell
# Run interactively in the terminal
.\ollama.exe run llama3.2

# Non-interactive / API test (non-streaming response):
curl http://localhost:11434/api/generate -H 'Content-Type: application/json' -d '{"model":"llama3.2","prompt":"Say hi","stream":false}'
```

Pull or create a model from a Modelfile (example):

```powershell
# Create a custom model from a Modelfile in the current directory
.\ollama.exe create my-custom-model -f Modelfile

# Pull a published model (if available in your registry/image provider)
.\ollama.exe pull gcr.io/some-repo/llama3.2:latest
```

Suggested local model names to try (common names used in examples across the workspace):

- llama3.2
- vicuna-13b
- guanaco-7b
- mistral-7b
- llama2-7b

Notes and tips:
- If a model is not listed in `/api/tags`, ensure the Ollama server is running (`ollama serve`) and check logs for startup errors.
- `stream: false` simplifies client code by returning a single JSON object. Use streaming only for incremental UIs.
- If you need an offline copy of a model, use `ollama pull` (if your environment/registry supports it) or `ollama create` with a Modelfile that references a local or cached artifact.

### Detected local models (live snapshot)

The environment currently has the following local models available (you can refresh this by running `scripts\list_models.ps1`):

- `mistral:7b` — ~4.07 GB, parameter_size: 7.2B, format: gguf, quantization: Q4_K_M
- `llama3.1:8b` — ~4.58 GB, parameter_size: 8.0B, format: gguf, quantization: Q4_K_M

To produce a markdown snapshot of the current local models, run the helper `scripts\export_local_models.ps1` which writes `LOCAL_MODELS.md` at the repo root.

## Post-edit checklist (required after making file changes)

Per repository rules, after editing files you should run the repository analysis locally. If you have the Codacy CLI installed, run it against the edited file(s). If you don't have it, use the helper script `scripts\codacy_check.ps1`.

- Run Codacy CLI analysis for the file(s) you edited and address issues reported by the tool.
- For dependency changes (package installs, requirements, etc.), run the security scanner (`trivy`) as part of the Codacy scan per project rules.
- Commit changes only after CI/lint hooks and Codacy checks pass locally.

If automation fails in your environment (for example, WSL is unavailable), run the commands manually or include a note in your PR describing why checks couldn't be run.

## Static server (quick demo for `demo-repository`)

Preview `Repos/demo-repository` locally with a simple static server. Pick one option below.

- Node (npm):

```powershell
cd 'E:\A.I. Development\Repos\demo-repository'
npm install
# serve is a small static server; install it temporarily with npx
npx serve -s .
```

- Python (built-in):

```powershell
cd 'E:\A.I. Development\Repos\demo-repository'
python -m http.server 8000
```

Open `http://localhost:5000` (for `serve`) or `http://localhost:8000` (Python) to preview the demo page.

## Helper scripts (quick helpers)

I added a few small PowerShell helpers in `scripts\` to make common tasks easier. They are intentionally tiny and safe; use them as convenience wrappers or read them to adapt for your environment.

- `scripts\list_models.ps1` — Queries the local Ollama HTTP API (`/api/tags`) and pretty-prints the JSON model list. Use this to confirm which models are available locally.

	Usage (PowerShell):

```powershell
cd 'E:\A.I. Development\scripts'
.\list_models.ps1
```

- `scripts\run_static_server.ps1` — Starts a demo static server for `Repos/demo-repository`. Supports two modes: `node` (runs `npx serve -s .`) or `python` (runs `python -m http.server 8000`).

	Usage (PowerShell):

```powershell
cd 'E:\A.I. Development\scripts'
.\run_static_server.ps1 -Mode node
# or
.\run_static_server.ps1 -Mode python
```

- `scripts\codacy_check.ps1` — Helper wrapper to run Codacy CLI analysis on a file or the whole repo. It attempts to locate a locally installed `codacy` CLI and runs `codacy analyze`. If the CLI isn't present, it prints instructions.

	Usage (PowerShell):

```powershell
cd 'E:\A.I. Development\scripts'
.\codacy_check.ps1 -FilePath '..\.github\copilot-instructions.md'
```

Notes:
- These scripts are lightweight and intended for developers running on Windows/PowerShell. Inspect them before running if you're on another OS.
- The repository still requires that Codacy analysis (and trivy for dependency changes) be run after edits per project rules. If the automated MCP-based analysis fails here, run `codacy analyze` locally or use `scripts\codacy_check.ps1`.

CI note:

- A GitHub Actions workflow `codacy-trivy.yml` runs Codacy analysis (container) and a Trivy filesystem scan on pull requests. If the CI job flags issues, fix them locally and re-run the checks before pushing.
- If the MCP-based analysis isn't available in your environment, use `scripts\codacy_check.ps1` or the Docker commands shown by the helper.

## Client examples (defensive)
Two small JS snippets: one that requests a non-streaming response and one that can handle streamed JSON objects.

Non-streaming (simple):

```javascript
async function ask(prompt) {
	const res = await fetch('http://localhost:11434/api/generate', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ model: 'llama3.2', prompt, stream: false })
	});
	const data = await res.json();
	// final text is in data.response
	return data.response || JSON.stringify(data);
}
```

Streaming (incremental UI updates — uses fetch + reader):

```javascript
async function askStream(prompt, onChunk) {
	const res = await fetch('http://localhost:11434/api/generate', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ model: 'llama3.2', prompt })
	});
	const reader = res.body.getReader();
	const decoder = new TextDecoder();
	let buf = '';
	while (true) {
		const { done, value } = await reader.read();
		if (done) break;
		buf += decoder.decode(value, { stream: true });
		// stream may deliver JSON objects separated by newlines — try to parse incremental chunks
		let idx;
		while ((idx = buf.indexOf('\n')) !== -1) {
			const line = buf.slice(0, idx).trim();
			buf = buf.slice(idx + 1);
			if (!line) continue;
			try {
				const obj = JSON.parse(line);
				if (obj.response) onChunk(obj.response, obj.done === true);
			} catch (e) {
				// ignore partial JSON
			}
		}
	}
}
```

- **Install:** `npm install`
- **Lint HTML:** `npm run lint` (uses `htmlhint`)
```
test: echo "Error: no test specified" && exit 1
lint: htmlhint **/*.html
```

**CI/CD:**
- On PR, GitHub Actions run HTML lint and link checks.
- See `.github/workflows/ci.yml`, `proof-html.yml`, `auto-assign.yml` for details.
- Do not edit `node_modules/` (see `DO_NOT_EDIT_NODE_MODULES.txt`).
- Document dev journey in `JOURNEY_LOG.md`.
- `index.html`, `about.html`: Main site content
- `package.json`: Scripts and dependencies

- **Pre-commit hooks:** All lint, format, and test hooks must pass before commit. Go-based hooks require Go toolchain installed and in PATH.
- **Makefile/PowerShell:** Use provided scripts for build, test, serve, backup, lint, format, setup, etc.

- After ANY file edit, IMMEDIATELY run Codacy CLI analysis for each edited file.
- If Codacy CLI is not installed, prompt user to install.

- Prefer reading existing clients/SDKs before writing HTTP calls.
- Use `make dev` or the package manager's `run dev` if present.

- Ollama: See all `README.md` and `docs/` for platform, API, and developer guides.
- demo-repository: See `PLAYBOOK.md`, `JOURNEY_LOG.md`, and `.github/workflows/` for workflow and automation details.
