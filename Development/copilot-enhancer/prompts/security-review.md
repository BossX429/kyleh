# Security Review Prompt

Use this prompt to perform security review of code changes.

## Prompt Template

```
Perform a comprehensive security review of the following code:

[PASTE CODE TO REVIEW HERE]

Security checklist:
1. Input Validation
   - Are all user inputs validated?
   - Are there SQL injection vulnerabilities?
   - Are there XSS vulnerabilities?
   - Is input sanitized before use?

2. Authentication & Authorization
   - Is authentication properly implemented?
   - Are credentials handled securely?
   - Is access control enforced?
   - Are permissions checked before operations?

3. Data Protection
   - Are sensitive data encrypted at rest?
   - Are sensitive data encrypted in transit?
   - Are API keys/secrets properly managed?
   - Is PII handled according to privacy requirements?

4. Error Handling
   - Are errors handled gracefully?
   - Do error messages leak sensitive info?
   - Are exceptions properly logged?
   - Are there denial-of-service risks?

5. Dependencies
   - Are dependencies from trusted sources?
   - Are dependency versions pinned?
   - Are there known vulnerabilities in dependencies?

6. Code Injection
   - Is eval/exec used? (should avoid)
   - Are system commands properly escaped?
   - Is user input used in dynamic code execution?

7. Logging & Monitoring
   - Are security events logged?
   - Are logs protected from tampering?
   - Are credentials excluded from logs?

Provide:
1. Security issues found (severity: critical/high/medium/low)
2. Recommended fixes for each issue
3. Security best practices to follow
4. Additional security tests to add
```

## Usage

1. Select code to review (especially changes touching security-critical areas)
2. Paste into template
3. Submit to GitHub Copilot
4. Review findings and implement fixes
5. Re-review after fixes applied

## High-Risk Code Areas

Always review these carefully:
- Authentication/authorization logic
- Database queries
- File operations
- Network operations
- Cryptography
- Session management
- API endpoints
- User input handling

## Security Tools

Run these tools as part of security review:
```bash
# Python security scanner
bandit -r .

# Dependency vulnerability check
pip-audit

# Secret scanning
git secrets --scan

# CodeQL analysis
codeql analyze
```
