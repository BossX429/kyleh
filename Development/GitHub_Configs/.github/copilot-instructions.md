# Copilot instructions for this repository (vscode-markdownlint)

Big picture
- VS Code extension that lints Markdown using markdownlint-cli2; runs in both desktop and web extension hosts.
- Entry: `extension.mjs` (ESM) → bundled by Webpack to `bundle` (desktop) and `bundle.web` (web). Activation: `onLanguage: markdown`.
- Settings live under `markdownlint.*`. Default disables MD013 (line length) unless overridden by user/workspace config.

Developer workflows
- Prereqs: Node >= 16, npm only (no lockfile). Install exactly like CI: `npm install --no-package-lock`.
- Lint source: `npm run lint`. Build: `npm run compile` (emits desktop and web bundles).
- Fast path tests: `npm test` → runs lint, compile, schema copy, unit/integration, then verifies a clean git diff.
- UI tests (Electron): `npm run test-ui` (via @vscode/test-electron, xvfb in CI). Web tests: `npm run test-web` (installs @vscode/test-web on demand).
- Update embedded schemas copied from deps: `npm run schema`.

Debugging
- Launch configs: `.vscode/launch.json` → "Launch Extension" (desktop) and "Launch Web Extension" (web, uses `--extensionDevelopmentKind=web`).

Project conventions
- Source is ESM `.mjs`; formatting via ESLint only (no Prettier). See `eslint.config.mjs` for tabs, double quotes, unicorn/stylistic rules; `vscode` import is allowlisted.
- Contributed commands (see `package.json → contributes.commands`): `markdownlint.fixAll`, `markdownlint.lintWorkspace`, `markdownlint.openConfigFile`, `markdownlint.toggleLinting`.
- Workspace lint opens a Terminal and uses the `$markdownlint` problem matcher.

Config + behavior
- `extension.mjs` resolves config files and globs (see `configFileNames`, `lintWorkspaceGlobs`), and ensures MD013 is disabled by default.
- Keep desktop and web behavior in sync; if you change config or rule resolution, verify both `bundle` and `bundle.web`.
- Config resolution (general): looks for standard markdownlint files in workspace root and directories of opened files; nearest file wins. Supports `.markdownlint.json[c]`, `.markdownlint.yaml`, and `package.json` → `markdownlint` field. Respects `.markdownlintignore` patterns.
 - Multi-root: workspace lint iterates roots; rules and ignores are resolved per-folder.

Config examples
- Repo `.markdownlint.jsonc` (reenable MD013 with a limit, tweak another rule):

```jsonc
{
	// Reenable line length with 100 cols
	"MD013": { "line_length": 100 },
	// Only flag duplicate headings among siblings
	"MD024": { "siblings_only": true }
}
```

- Or configure in `package.json` under `markdownlint`:

```jsonc
{
	"markdownlint": {
		"MD013": { "line_length": 100 },
		"MD033": false // allow inline HTML
	}
}
```

- Ignore patterns in `.markdownlintignore`:

```
dist/
out/
**/vendor/**
```

CI quick facts
- Workflows run: setup-node → `npm install --no-package-lock` → `npm test` → UI tests under xvfb. Link checking (linkinator) and spell checking (`.github/dictionary.txt`) gate PRs.

Key files
- `extension.mjs` (commands, diagnostics, config resolution), `webpack.config.js` (bundles), `eslint.config.mjs`, `test-ui/run-tests.mjs`, `.vscode/launch.json`, `package.json`.

Safe-change checklist
- Run `npm test` before/after `npm run compile`; expect no diffs (`git diff --exit-code`).
- Adding a command? Declare in `package.json → contributes.commands`, implement in `extension.mjs`, and wire menus if needed.
- Adding deps? Ensure desktop+web compatibility and adjust Webpack shims when required.

Add a command (quick steps)
1) `package.json → contributes.commands`: add `{ "command": "markdownlint.myCommand", "title": "Markdownlint: My Command" }`.
2) In `extension.mjs`, register on activate: `vscode.commands.registerCommand("markdownlint.myCommand", async () => {/* ... */});` and push to `context.subscriptions`.
3) Add to menus if needed (`contributes.menus`) and include in README.

Troubleshooting
- No diagnostics? Check the active file language is Markdown and the extension is activated; run `Markdownlint: Toggle Linting` to confirm.
- Config ignored? Confirm the config file is in the workspace or file directory and not excluded by `.markdownlintignore`.
- Diff after tests? Re-run `npm run schema` and `npm run compile`, then commit regenerated artifacts if intentional.

Licensing and deps (free software)
- Use only free/open-source dependencies compatible with this repo (prefer MIT/Apache-2.0/ISC/BSD).
- Avoid strong-copyleft (e.g., GPL/LGPL/AGPL) unless explicitly approved; ensure web bundling permits redistribution.
- If adding a dep, verify license in `package.json` and on npm; document rationale in PR description.

Dependency verification (PRs)
- Link the npm package page and version; justify why the dep is needed instead of a local utility.
- License: include SPDX id; confirm it’s in the allowlist (MIT, Apache-2.0, ISC, BSD-2-Clause, BSD-3-Clause, CC0-1.0, Unlicense). Paste a short license snippet if uncommon.
- Browser/runtime: confirm ESM support and no Node-only APIs at runtime (fs, path, process, child_process). If shims are required, note the plan for `webpack.config.js`.
- Packaging: prefer tree-shakable modules (`sideEffects: false`) and small footprint; avoid bundling CLIs or transitive heavy deps.
- Transitives: glance at transitive deps on the npm page; avoid introducing non-free or problematic licenses via transitive chains.
- Security: ensure there are no known critical advisories blocking install; brief note is enough.

CI license allowlist
- CI enforces allowed licenses for production and dev deps via `.github/workflows/license-allowlist.yml`.
- Allowed SPDX are defined in `.github/license-allowlist.json`. Update this list in a PR if policy changes.
- Local check (production):
	- `npx license-checker-rseidelsohn --production --summary --json > licenses.prod.json`
	- `node scripts/check-licenses.js licenses.prod.json`
- Local check (development):
	- `npx license-checker-rseidelsohn --development --summary --json > licenses.dev.json`
	- `node scripts/check-licenses.js licenses.dev.json`
- Tip: Use `--development` (not `--dev` or `--devnode`). A deprecation warning from a transitive npm lib is harmless.
 - CI pins the CLI version for repeatability: `license-checker-rseidelsohn@4.3.0`. CI uploads reports as artifacts and includes a step summary.
- Optional npm scripts (add to package.json):
	- `"license:prod": "npx license-checker-rseidelsohn --production --summary --json > licenses.prod.json && node scripts/check-licenses.js licenses.prod.json"`
	- `"license:dev": "npx license-checker-rseidelsohn --development --summary --json > licenses.dev.json && node scripts/check-licenses.js licenses.dev.json"`
- Exceptions: you can allow specific packages via `.github/license-allowlist.json` → `allowedPackages` (exact) or `allowedPackagePatterns` (regex). Use sparingly and justify in PRs.
	- Exact format example: `"left-pad@1.3.0"` or `"left-pad@1"` or `"left-pad"` (match by full name as returned by license-checker)
	- Pattern example: `"^@org\\/internal-.*@"` (full package spec is matched)
	- CI publishes license JSON reports as artifacts and writes a step summary for quick triage.