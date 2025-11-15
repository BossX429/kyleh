# Code Refactoring Prompt

Use this prompt to refactor code while maintaining functionality.

## Prompt Template

```
Refactor the following Python code to improve:
- Readability
- Maintainability
- Performance (if applicable)
- Type safety
- Error handling

[PASTE CODE TO REFACTOR HERE]

Refactoring guidelines:
1. Extract complex logic into separate functions
2. Use descriptive variable and function names
3. Add type hints to all function signatures
4. Improve error handling with specific exceptions
5. Reduce code duplication (DRY principle)
6. Follow Single Responsibility Principle
7. Maintain existing functionality (no breaking changes)
8. Add docstrings to new functions
9. Use Python idioms and best practices
10. Consider edge cases and add validation

Provide:
1. Refactored code
2. Brief explanation of changes made
3. Any potential issues or considerations
4. Suggestions for additional improvements

Code style:
- Use black formatting (100 char line length)
- Follow PEP 8 conventions
- Use meaningful names over comments
- Keep functions focused and small (< 50 lines)
```

## Usage

1. Identify code that needs refactoring
2. Paste code into template
3. Submit to GitHub Copilot
4. Review refactored code carefully
5. Run existing tests to ensure functionality preserved
6. Update or add tests if behavior changed

## Refactoring Checklist

After refactoring, verify:
- [ ] All existing tests still pass
- [ ] No breaking changes to public API
- [ ] Type hints added/updated
- [ ] Docstrings added/updated
- [ ] Code coverage maintained or improved
- [ ] Performance not degraded
- [ ] Error handling improved
- [ ] Code is more readable
