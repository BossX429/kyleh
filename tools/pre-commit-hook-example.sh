#!/bin/bash
# Example pre-commit hook for Unicode character checking
# 
# To install:
#   cp tools/pre-commit-hook-example.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# This hook checks for suspicious Unicode characters before allowing commits.

echo "Checking for Unicode characters..."

# Get list of files to be committed
FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.(py|md|txt|js|json|yml|yaml)$')

if [ -z "$FILES" ]; then
    echo "✓ No text files to check"
    exit 0
fi

# Check for suspicious Unicode patterns
SUSPICIOUS_PATTERNS=(
    "ZERO WIDTH"
    "RIGHT-TO-LEFT"
    "LEFT-TO-RIGHT"
    "VARIATION SELECTOR"
)

HAS_SUSPICIOUS=false

for FILE in $FILES; do
    # Use find_unicode.py to check this file
    if [ -f "$FILE" ]; then
        OUTPUT=$(python3 tools/find_unicode.py --pattern "$(basename $FILE)" --directory "$(dirname $FILE)" 2>/dev/null)
        
        # Check for suspicious patterns
        for PATTERN in "${SUSPICIOUS_PATTERNS[@]}"; do
            if echo "$OUTPUT" | grep -q "$PATTERN"; then
                echo "⚠️  Suspicious Unicode in $FILE: $PATTERN"
                HAS_SUSPICIOUS=true
            fi
        done
    fi
done

if [ "$HAS_SUSPICIOUS" = true ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Suspicious Unicode characters detected"
    echo ""
    echo "Please review the files listed above and remove suspicious Unicode."
    echo "See UNICODE_CHARACTERS.md for guidelines."
    echo ""
    echo "To bypass this check (not recommended):"
    echo "  git commit --no-verify"
    exit 1
fi

echo "✓ No suspicious Unicode found"
exit 0
