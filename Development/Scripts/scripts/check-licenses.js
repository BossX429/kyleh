#!/usr/bin/env node
/*
 Simple license allowlist check using license-checker-rseidelsohn output.
 Usage:
   node scripts/check-licenses.js path/to/licenses.json
 Exits 1 if any dependency has a license outside the allowlist.
*/
const fs = require("fs");
const path = require("path");

const [, , licensesPath = "licenses.json"] = process.argv;
const allowlistPath = path.join(".github", "license-allowlist.json");

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

const {
  allowedSpdx,
  allowedPackages = [],
  allowedPackagePatterns = [],
} = readJson(allowlistPath);
const data = readJson(licensesPath);

const allowed = new Set(allowedSpdx);
const violations = [];
const total = Object.keys(data).length;

for (const [name, info] of Object.entries(data)) {
  // Exceptions: exact matches or any regex pattern match
  if (
    allowedPackages.includes(name) ||
    allowedPackagePatterns.some((p) => new RegExp(p).test(name))
  ) {
    continue;
  }
  const licArr = Array.isArray(info.licenses) ? info.licenses : [info.licenses];
  // Some packages report complex expressions; split on OR/AND, commas
  const flat = licArr.flatMap((l) =>
    String(l)
      .split(/\s*(?:\(|\)|\s+OR\s+|\s+AND\s+|,|\||\/)\s*/i)
      .filter(Boolean)
  );
  const allAllowed = flat.every((l) => allowed.has(l));
  if (!allAllowed) violations.push({ name, licenses: licArr });
}

const summaryPath = process.env.GITHUB_STEP_SUMMARY;
if (violations.length) {
  const header =
    "Disallowed licenses found (see .github/license-allowlist.json):";
  console.error(header);
  const lines = violations.map(
    (v) => ` - ${v.name}: ${JSON.stringify(v.licenses)}`
  );
  for (const line of lines) console.error(line);
  if (summaryPath) {
    try {
      fs.appendFileSync(
        summaryPath,
        `\n### License check failed\n\nScanned packages: ${total}\n\n${header}\n\n${lines.join(
          "\n"
        )}\n`
      );
    } catch {}
  }
  process.exit(1);
}
console.log(`All licenses allowed. Scanned packages: ${total}.`);
if (summaryPath) {
  try {
    fs.appendFileSync(
      summaryPath,
      `\n### License check passed\n\nAll licenses allowed. Scanned packages: ${total}.\n`
    );
  } catch {}
}
