---
name: django-core
description: Core Django best practices, architecture patterns, and conventions for clean, maintainable applications. Use this skill for any Django-related task involving models, views, templates, ORM, settings, or general project structure.
---

# Django Core Best Practices

**Always follow these guidelines:**

### Models
- Use `UUIDField(primary_key=True)` for new models (unless legacy constraints exist).
- Add `verbose_name` and `verbose_name_plural` on every model and field.
- Implement a meaningful `__str__()` method.
- Use custom `Manager` classes for complex queries.
- Add `Meta` class with proper `ordering`, `indexes`, and constraints.
- Use `select_related()` / `prefetch_related()` when querying to avoid N+1 issues.

### Views & URLs
- Prefer **Class-Based Views** (especially `ListView`, `DetailView`, `CreateView`, etc.) for most cases.
- Keep views thin — move business logic to models, services, or use-cases.
- Use `LoginRequiredMixin`, `PermissionRequiredMixin`, and `UserPassesTestMixin`.
- Use `reverse_lazy()` for redirects in class-based views.

### Forms & Validation
- Always validate data using Django Forms or DRF Serializers.
- Prefer ModelForms when working directly with models.
- Never trust raw user input.

### General Rules
- Use Django’s built-in tools first (admin, auth, sessions, etc.).
- Follow the “Fat Models, Thin Views” principle.
- Use `django-environ` or `python-decouple` for configuration.
- Enable `USE_TZ=True` and work with timezone-aware datetimes.
- Write docstrings for models, views, and complex functions.

**When to use this skill:** Any task involving Django models, views, admin, settings, or general development.