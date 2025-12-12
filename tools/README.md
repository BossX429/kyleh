# Unicode Management Tools

This directory contains utilities for finding, analyzing, and managing Unicode characters in the repository.

## Tools Overview

### 1. find_unicode.py

Scan the repository for non-ASCII Unicode characters and generate detailed reports.

**Usage:**
```bash
# Scan current directory
python3 tools/find_unicode.py

# Scan specific directory
python3 tools/find_unicode.py --directory /path/to/repo

# Show detailed file-by-file report
python3 tools/find_unicode.py --detailed

# Limit detailed report to top 5 files
python3 tools/find_unicode.py --detailed --max-files 5

# Scan only Python files
python3 tools/find_unicode.py --pattern "*.py"

# Scan multiple file types
python3 tools/find_unicode.py --pattern "*.py" --pattern "*.md"
```

**Output:**
- Summary of all unique Unicode characters found
- Character codepoints, names, and categories
- Total files and lines containing Unicode
- Optional detailed file-by-file breakdown

**Example:**
```bash
$ python3 tools/find_unicode.py --detailed --max-files 3

Scanning directory: /home/user/kyleh
File patterns: *.py, *.md, *.txt, *.js, *.json, *.yml, *.yaml
================================================================================
UNICODE CHARACTER SUMMARY
================================================================================

Total files with Unicode: 15
Total lines with Unicode: 142
Unique Unicode characters: 38

================================================================================
ALL UNICODE CHARACTERS FOUND
================================================================================

Character: '→'
  Codepoint: U+2192 (decimal: 8594)
  Name: RIGHTWARDS ARROW
  Category: Sm
  Occurrences: 3 location(s)
...
```

### 2. test_unicode_support.py

Test if your terminal/environment supports the Unicode characters used in the repository.

**Usage:**
```bash
python3 tools/test_unicode_support.py
```

**What it does:**
- Displays all Unicode characters used in the repository
- Shows character codes and names
- Provides visual examples of usage
- Helps identify rendering issues in your environment

**Example Output:**
```
================================================================================
UNICODE SUPPORT TEST
================================================================================

Testing Unicode characters used in this repository...
If you see placeholder boxes (□) or question marks (?), 
your terminal doesn't fully support these characters.

✓ System encoding: UTF-8

================================================================================
EMOJIS (30 characters)
================================================================================
  🎯  U+1F3AF  Direct Hit
  🎓  U+1F393  Graduation Cap
  🐛  U+1F41B  Bug
  ...
```

### 3. unicode_to_ascii.py

Convert files with Unicode characters to ASCII-only versions for legacy environments.

**Usage:**
```bash
# Convert a single file
python3 tools/unicode_to_ascii.py input.md output.md

# Overwrite existing output file
python3 tools/unicode_to_ascii.py input.md output.md --force

# Show character mappings
python3 tools/unicode_to_ascii.py --show-mappings
```

**Conversion Examples:**
- `🎯 Overview` → `[TARGET] Overview`
- `✅ Completed` → `[x] Completed`
- `├── file.py` → `|- file.py`
- `→ next` → `-> next`

**Use Cases:**
- Creating ASCII versions for legacy terminals
- Generating text for automated parsers
- Email-friendly documentation
- Plain text logs

### 4. generate_unicode_docs.py (Future)

Auto-generate Unicode documentation based on current repository usage.

## Quick Start

### Find all Unicode in repository:
```bash
cd /path/to/kyleh
python3 tools/find_unicode.py --detailed
```

### Test your terminal support:
```bash
python3 tools/test_unicode_support.py
```

### Convert a file to ASCII:
```bash
python3 tools/unicode_to_ascii.py README.md README_ascii.md
```

## Integration with Development Workflow

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check for suspicious Unicode characters

python3 tools/find_unicode.py --pattern "*.py" | grep -E "ZERO WIDTH|VARIATION SELECTOR" && {
    echo "Error: Suspicious Unicode characters detected"
    exit 1
}
```

### CI/CD Pipeline

Add to GitHub Actions workflow:
```yaml
- name: Check Unicode usage
  run: |
    python3 tools/find_unicode.py > unicode_report.txt
    cat unicode_report.txt
```

### Documentation Generation

```bash
# Generate current Unicode usage report
python3 tools/find_unicode.py --detailed > docs/unicode_usage.txt
```

## Common Use Cases

### 1. Finding Hidden Unicode
```bash
# Find all non-visible Unicode characters
python3 tools/find_unicode.py | grep -E "ZERO WIDTH|VARIATION|SPACE"
```

### 2. Auditing Code Files
```bash
# Check only Python code
python3 tools/find_unicode.py --pattern "*.py" --detailed
```

### 3. Documentation Review
```bash
# Check markdown files
python3 tools/find_unicode.py --pattern "*.md" --detailed
```

### 4. Creating ASCII Versions
```bash
# Convert all markdown files
for file in *.md; do
    python3 tools/unicode_to_ascii.py "$file" "ascii_${file}"
done
```

## Character Categories

The tools recognize several Unicode character categories:

- **Emojis**: Decorative pictographs (🎯, 🔒, 🚀)
- **Check Marks**: Status indicators (✅, ✓, ✗, ❌)
- **Box Drawing**: ASCII art (├, ─, │, └)
- **Arrows**: Directional symbols (→)
- **Special**: Invisible or formatting characters

## Best Practices

### Do:
- ✅ Use `find_unicode.py` before major releases
- ✅ Run `test_unicode_support.py` on new environments
- ✅ Keep Unicode usage documented
- ✅ Use Unicode in user-facing output
- ✅ Provide ASCII alternatives for critical docs

### Don't:
- ❌ Use Unicode in API keys or tokens
- ❌ Mix similar-looking Unicode characters (security risk)
- ❌ Use invisible Unicode in code
- ❌ Rely solely on Unicode for critical information

## Troubleshooting

### Problem: Characters show as boxes (□)
**Solution**: Your terminal font doesn't support emoji. Install a font like:
- Noto Color Emoji (Linux)
- Apple Color Emoji (macOS)
- Segoe UI Emoji (Windows)

### Problem: Scripts fail with encoding errors
**Solution**: Ensure your system locale supports UTF-8:
```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

### Problem: Need ASCII version for legacy system
**Solution**: Use `unicode_to_ascii.py` to convert files:
```bash
python3 tools/unicode_to_ascii.py input.md output_ascii.md
```

## Contributing

When adding new Unicode characters to the repository:

1. Run `find_unicode.py` to verify additions
2. Update `UNICODE_CHARACTERS.md` if needed
3. Test with `test_unicode_support.py`
4. Add mappings to `unicode_to_ascii.py` if appropriate

## References

- [UNICODE_CHARACTERS.md](../UNICODE_CHARACTERS.md) - Full Unicode usage documentation
- [Unicode Standard](https://unicode.org/)
- [Python Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)

## Support

For issues or questions about Unicode in this repository:
1. Check [UNICODE_CHARACTERS.md](../UNICODE_CHARACTERS.md)
2. Run diagnostic tools in this directory
3. Open an issue on GitHub
