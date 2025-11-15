# Documentation Generation Prompt

Use this prompt to generate comprehensive documentation for Python modules.

## Prompt Template

```
Generate comprehensive documentation for the following Python module:

[PASTE MODULE CODE HERE]

Requirements:
- Use Google-style docstrings
- Document all public functions, classes, and methods
- Include parameter types and return types
- Add usage examples for main functionality
- Document exceptions that can be raised
- Include "See Also" sections for related functionality
- Add module-level docstring explaining purpose

Documentation format:
```python
\"\"\"
Brief one-line summary.

Extended description with more details about what this module/function does.
Explain the purpose, use cases, and important notes.

Args:
    param_name (type): Description of the parameter.
    another_param (type, optional): Description. Defaults to value.

Returns:
    return_type: Description of what is returned.

Raises:
    ExceptionType: Description of when this exception is raised.

Example:
    >>> from module import function
    >>> result = function(param="value")
    >>> print(result)
    Expected output

See Also:
    related_function: Related functionality
    ModuleName: Related module

Note:
    Important notes or warnings for users.
\"\"\"
```
```

## Usage

1. Select the module, class, or function to document
2. Replace `[PASTE MODULE CODE HERE]` with your code
3. Submit to GitHub Copilot
4. Review generated documentation for accuracy
5. Ensure examples are tested and working

## Best Practices

- Keep docstrings concise but complete
- Use concrete examples in usage sections
- Document edge cases and limitations
- Update docs when code changes
- Link to related documentation in README.md or API.md
