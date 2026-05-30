---
name: Django Core Best Practices
description: Guidelines for writing clean, idiomatic Django code
---

# Django Development Standards

## Models
- Use descriptive `verbose_name` and `verbose_name_plural`
- Add `__str__` method
- Use custom managers for complex queries
- Prefer `UUIDField` as primary key for new models

## Views
- Prefer Class-Based Views
- Keep views thin (business logic elsewhere)
- Use LoginRequiredMixin / PermissionRequiredMixin

## General
- Use `reverse_lazy` for redirects
- Handle exceptions gracefully
- Log important actions
- Write tests for every new feature