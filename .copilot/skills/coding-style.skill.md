---
name: coding-style
description: Code style, formatting, and Python/Django conventions for this project.
---

# Coding Style & Conventions

- Follow PEP 8.
- Use `black` for formatting and `ruff` for linting (if configured).
- Sort imports with `isort`.
- Use meaningful variable and function names.
- Keep functions short (< 50 lines when possible).
- Add type hints for new code.
- Use f-strings for string formatting.
- Avoid `except: pass` — catch specific exceptions.

**Django-specific:**
- Use consistent naming: `snake_case` for everything.
- Group imports: standard library → third-party → local.
- Add helpful comments for non-obvious logic.