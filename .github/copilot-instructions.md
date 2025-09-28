# Copilot & AI Agent Instructions – Unified Workspace Guide

## Workspace Overview
This workspace contains two major projects:
- **Ollama**: Modular LLM server, desktop app, API, model runners, Go/JS/Python integrations, and developer docs.
- **demo-repository**: HTML/JS demo site with strict workflow automation, CI/CD, and onboarding for new contributors.

All automation, linting, formatting, pre-commit, CI, and security checks are enabled by default. All agents and contributors must follow these rules for every file and workflow.

---

## Ollama: Key Workflows & Structure
- **Build core binary:** `go build .` (from repo root)
- **Run server:** `./ollama serve`
- **Run a model:** `./ollama run <model>`
- **Desktop app (macOS):** Build Go binary, then `npm install && npm start` in `macapp/`
- **Windows installer:** `powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1`
- **Integration tests:** `go test -tags=integration ./...` (see `integration/README.md`)
- **Vendoring llama.cpp:** Use `make -f Makefile.sync apply-patches` and follow `llama/README.md` for patch/merge workflow.
- **Model customization:** Use `Modelfile` with `FROM` and `PARAMETER` instructions, then `ollama create <name> -f Modelfile`.
- **REST API:** Exposed at `localhost:11434` (see `docs/api.md`).
- **Model management:** `ollama pull`, `ollama rm`, `ollama cp`, `ollama list`, `ollama ps`, `ollama stop`.
- **Integration tests** default to a small model, override with `OLLAMA_TEST_DEFAULT_MODEL`.
- **Test against running server:** Set `OLLAMA_TEST_EXISTING` and `OLLAMA_HOST` env vars.

**Key Directories & Files:**
- `README.md` (root): Quickstart, CLI, REST API, and model library usage
- `runner/`: Minimal HTTP server for model inference
- `integration/`: Integration tests
- `docs/`: Developer, API, and platform-specific documentation
- `api/examples/`: Go code samples for API usage
- `macapp/`, `app/`: Desktop app
- `llama/`: Go bindings and vendoring for `llama.cpp` and `ggml`

---

## demo-repository: Key Workflows & Structure
- **Install:** `npm install`
- **Lint HTML:** `npm run lint` (uses `htmlhint`)
- **Edit cycle:** Edit → Save → `npm run lint` → Commit → Push → PR/Merge
- **Run locally:** Use your package manager’s dev script if present
- **Branching:** `git checkout -b feat/<name>` for features
- **Document dev journey:** in `JOURNEY_LOG.md`

**Scripts (from package.json):**
```
test: echo "Error: no test specified" && exit 1
lint: htmlhint **/*.html
```

**CI/CD:**
- On PR, GitHub Actions run HTML lint and link checks.
- See `.github/workflows/ci.yml`, `proof-html.yml`, `auto-assign.yml` for details.

**Conventions:**
- Do not edit `node_modules/` (see `DO_NOT_EDIT_NODE_MODULES.txt`).
- Document dev journey in `JOURNEY_LOG.md`.

**Key Files:**
- `index.html`, `about.html`: Main site content
- `package.json`: Scripts and dependencies
- `PLAYBOOK.md`: Workflow summary
- `JOURNEY_LOG.md`: Dev history
- `.github/workflows/`: CI/CD config

---

## Automation, Pre-commit, and Security (All Projects)
- **Pre-commit hooks:** All lint, format, and test hooks must pass before commit. Go-based hooks require Go toolchain installed and in PATH.
- **Makefile/PowerShell:** Use provided scripts for build, test, serve, backup, lint, format, setup, etc.
- **CI/CD:** All PRs run full lint, format, and security checks. See `.github/workflows/` for details.
- **Docker:** Use `Dockerfile` for container builds. `.env.example` for environment variables.
- **Dependabot:** Automated dependency updates via `.github/dependabot.yml`.
- **Issue/PR templates:** Use `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md` for all contributions.

---

## Codacy MCP Server Rules (Critical)
- After ANY file edit, IMMEDIATELY run Codacy CLI analysis for each edited file.
- If Codacy CLI is not installed, prompt user to install.
- After any dependency install or package manager operation, run Codacy CLI with `trivy` for security scan.
- If vulnerabilities are found, STOP and fix before continuing.
- Do not edit `node_modules/` or run Codacy CLI for code coverage/duplication.
- If Codacy MCP is unreachable, suggest user reset MCP or check Copilot > MCP settings.

---

## Project-Specific Conventions & Best Practices
- Prefer reading existing clients/SDKs before writing HTTP calls.
- Use `make dev` or the package manager's `run dev` if present.
- For Ollama, see `docs/api.md` for REST API and model management.
- For demo-repository, always run `npm run lint` before commit and push.
- Document all workflow changes and onboarding improvements in this file.

---

## References & Further Reading
- Ollama: See all `README.md` and `docs/` for platform, API, and developer guides.
- demo-repository: See `PLAYBOOK.md`, `JOURNEY_LOG.md`, and `.github/workflows/` for workflow and automation details.
- Codacy: `.github/instructions/codacy.instructions.md` for full MCP rules.

---

**Update this file as workflows, automation, or conventions evolve.**
