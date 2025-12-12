# Unicode Tools - Usage Examples

This document provides practical examples of using the Unicode management tools.

## Quick Start

### 1. Find all Unicode in the repository

```bash
cd /path/to/kyleh
python3 tools/find_unicode.py
```

**Output:**
```
Scanning directory: /path/to/kyleh
File patterns: *.py, *.md, *.txt, *.js, *.json, *.yml, *.yaml
================================================================================
UNICODE CHARACTER SUMMARY
================================================================================

Total files with Unicode: 20
Total lines with Unicode: 367
Unique Unicode characters: 39

Character: '🎯'
  Codepoint: U+1F3AF (decimal: 127919)
  Name: DIRECT HIT
  Category: So
  Occurrences: 8 location(s)
...
```

### 2. Get detailed file-by-file report

```bash
python3 tools/find_unicode.py --detailed --max-files 5
```

Shows the top 5 files with the most Unicode usage, including line numbers and context.

### 3. Test your terminal's Unicode support

```bash
python3 tools/test_unicode_support.py
```

**Output:**
```
================================================================================
UNICODE SUPPORT TEST
================================================================================

✓ System encoding: utf-8

EMOJIS (30 characters)
  🎯  U+1F3AF  Direct Hit
  🔒  U+1F512  Lock
  🚀  U+1F680  Rocket
...
```

### 4. Convert a file to ASCII

```bash
python3 tools/unicode_to_ascii.py README.md README_ascii.md
```

**Before:**
```markdown
## 🎯 Overview
- ✅ Feature complete
- 🚀 Ready to deploy
```

**After:**
```markdown
## [TARGET] Overview
- [x] Feature complete
- [DEPLOY] Ready to deploy
```

## Advanced Examples

### Find Unicode in specific file types

**Python files only:**
```bash
python3 tools/find_unicode.py --pattern "*.py" --detailed
```

**Multiple file types:**
```bash
python3 tools/find_unicode.py \
  --pattern "*.py" \
  --pattern "*.md" \
  --pattern "*.txt"
```

### Search specific directory

```bash
python3 tools/find_unicode.py --directory SecurityBot/ --detailed
```

### Export results to file

```bash
python3 tools/find_unicode.py --detailed > unicode_audit_$(date +%Y%m%d).txt
```

### Check for suspicious Unicode

```bash
python3 tools/find_unicode.py | grep -E "ZERO WIDTH|VARIATION SELECTOR|RIGHT-TO-LEFT"
```

## Batch Operations

### Convert multiple files to ASCII

```bash
# Convert all markdown files in a directory
for file in docs/*.md; do
    output="ascii_versions/$(basename $file)"
    python3 tools/unicode_to_ascii.py "$file" "$output"
done
```

### Generate Unicode report for each subdirectory

```bash
for dir in SecurityBot Development system_monitor; do
    echo "Checking $dir..."
    python3 tools/find_unicode.py --directory "$dir" > "reports/${dir}_unicode.txt"
done
```

## Integration Examples

### Pre-commit Hook

Install the pre-commit hook:

```bash
cp tools/pre-commit-hook-example.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Now every commit will be checked for suspicious Unicode.

### CI/CD Integration (GitHub Actions)

The repository includes `.github/workflows/unicode-check.yml` which:
- Runs on every PR
- Generates Unicode report
- Comments on PR with summary
- Fails if suspicious Unicode detected

**Trigger manually:**
```bash
# Via GitHub UI: Actions → Unicode Character Check → Run workflow
```

### Custom Script Integration

```python
#!/usr/bin/env python3
import subprocess
import json

# Run find_unicode.py and capture output
result = subprocess.run(
    ['python3', 'tools/find_unicode.py'],
    capture_output=True,
    text=True
)

# Parse the output
if 'Total files with Unicode: 0' in result.stdout:
    print("✓ No Unicode found")
else:
    print("Unicode characters detected - see report")
    print(result.stdout)
```

## Real-World Scenarios

### Scenario 1: Preparing for legacy system deployment

**Problem:** Need ASCII-only versions of docs for legacy terminal access.

**Solution:**
```bash
# Convert all documentation to ASCII
mkdir ascii_docs
for file in *.md docs/*.md; do
    if [ -f "$file" ]; then
        outfile="ascii_docs/$(basename $file)"
        python3 tools/unicode_to_ascii.py "$file" "$outfile"
    fi
done
```

### Scenario 2: Auditing before release

**Problem:** Need to ensure no problematic Unicode in the codebase.

**Solution:**
```bash
# Generate comprehensive report
python3 tools/find_unicode.py --detailed > release_unicode_audit.txt

# Check for issues
if grep -qE "ZERO WIDTH|VARIATION SELECTOR" release_unicode_audit.txt; then
    echo "❌ Problematic Unicode found - review required"
    exit 1
else
    echo "✅ Unicode audit passed"
fi
```

### Scenario 3: New developer onboarding

**Problem:** New developer's terminal doesn't show emojis correctly.

**Solution:**
```bash
# Test their environment
python3 tools/test_unicode_support.py

# If issues found, convert their local docs to ASCII
python3 tools/unicode_to_ascii.py README.md README_local.md
python3 tools/unicode_to_ascii.py CONTRIBUTING.md CONTRIBUTING_local.md
```

### Scenario 4: Security audit

**Problem:** Need to find all Unicode usage for security review.

**Solution:**
```bash
# Full audit with context
python3 tools/find_unicode.py --detailed --context > security_audit.txt

# Extract files by Unicode count
echo "=== Files with most Unicode ===" >> security_audit.txt
grep "Lines with Unicode:" security_audit.txt | sort -rn -k4 >> security_audit.txt

# Check for look-alike characters
grep -E "LATIN CAPITAL|CYRILLIC|GREEK" security_audit.txt
```

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Ensure you're in the repository root
cd /path/to/kyleh

# Check Python version
python3 --version  # Should be 3.8+

# Try with full path
python3 /path/to/kyleh/tools/find_unicode.py
```

### Issue: Output shows boxes instead of emojis

**Cause:** Your terminal doesn't support emoji fonts.

**Solutions:**
1. **Install emoji font:**
   - Ubuntu: `sudo apt install fonts-noto-color-emoji`
   - macOS: Already included
   - Windows: Install Windows Terminal

2. **Use ASCII version:**
   ```bash
   python3 tools/unicode_to_ascii.py input.md output.md
   ```

### Issue: Tool runs slowly on large repository

**Solution:**
```bash
# Limit to specific directories
python3 tools/find_unicode.py --directory src/

# Limit to specific file types
python3 tools/find_unicode.py --pattern "*.py"

# Combine both
python3 tools/find_unicode.py --directory src/ --pattern "*.py"
```

### Issue: Need to find specific Unicode character

**Solution:**
```bash
# Using grep with hex code
grep -r $'\xF0\x9F\x8E\xAF' .  # Finds 🎯

# Using find_unicode.py and grep
python3 tools/find_unicode.py | grep "U+1F3AF"

# Using Python
python3 -c "print('\U0001F3AF' in open('file.md').read())"
```

## Custom Mappings

### Adding custom Unicode-to-ASCII mappings

Edit `tools/unicode_to_ascii.py`:

```python
UNICODE_TO_ASCII = {
    # Your custom mappings
    '🔥': '[FIRE]',
    '💾': '[SAVE]',
    '📂': '[FOLDER]',
    
    # Existing mappings...
    '🎯': '[TARGET]',
    # ...
}
```

Then run:
```bash
python3 tools/unicode_to_ascii.py input.md output.md
```

## Performance Tips

### For large repositories

1. **Use specific patterns:**
   ```bash
   # Instead of scanning everything
   python3 tools/find_unicode.py --pattern "*.py" --pattern "*.md"
   ```

2. **Exclude directories:**
   The tool automatically excludes `.git`, `node_modules`, etc.

3. **Parallel processing:**
   ```bash
   # Check multiple directories in parallel
   python3 tools/find_unicode.py --directory src/ > src_report.txt &
   python3 tools/find_unicode.py --directory docs/ > docs_report.txt &
   wait
   ```

### For frequent checks

Create a shell alias:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias check-unicode='python3 tools/find_unicode.py'
alias test-unicode='python3 tools/test_unicode_support.py'
alias convert-unicode='python3 tools/unicode_to_ascii.py'
```

Then:
```bash
check-unicode --detailed
test-unicode
convert-unicode input.md output.md
```

## Additional Resources

- [UNICODE_CHARACTERS.md](../UNICODE_CHARACTERS.md) - Complete Unicode documentation
- [tools/README.md](README.md) - Tool documentation
- [Unicode Standard](https://unicode.org/) - Official Unicode reference
- [Python Unicode HOWTO](https://docs.python.org/3/howto/unicode.html) - Python Unicode guide

## Contributing

Found a useful example? Add it to this document!

```bash
# Fork the repo, add your example, and submit a PR
git checkout -b add-unicode-example
# Edit tools/EXAMPLES.md
git add tools/EXAMPLES.md
git commit -m "docs: Add example for [use case]"
git push origin add-unicode-example
```
