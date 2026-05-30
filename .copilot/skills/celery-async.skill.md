---
name: celery-async
description: Best practices for asynchronous tasks using Celery in Django projects.
---

# Celery & Async Tasks Best Practices

- Keep tasks idempotent when possible.
- Use `bind=True` and proper error handling in tasks.
- Set reasonable timeouts and retries.
- Use `django-celery-beat` for periodic tasks.
- Log important events inside tasks.
- Never put heavy computation or long-running operations in request-response cycle — offload to Celery.

Use this skill for any task involving background jobs, email sending, data processing, etc.