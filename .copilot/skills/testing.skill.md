---
name: testing
description: Testing standards and patterns for Django projects. Use when writing, updating, or running tests.
---

# Testing Best Practices for Django

**Philosophy:**
- Write tests for every new feature and bug fix.
- Aim for high coverage on business logic.
- Test both happy paths and edge cases.

**Preferred Tools:**
- Use `pytest` + `pytest-django` if configured.
- Fall back to Django’s `TestCase` / `APITestCase` otherwise.

**Guidelines:**
- Use factories (`factory_boy` or `model_baker`) instead of creating objects manually.
- Use `TestCase` for database tests, `SimpleTestCase` when no DB is needed.
- Mock external services and Celery tasks.
- Test permissions, validation errors, and authentication flows.
- Name tests clearly: `test_method_scenario_expectedresult`.

**When reviewing code:** Always check if new functionality has corresponding tests.