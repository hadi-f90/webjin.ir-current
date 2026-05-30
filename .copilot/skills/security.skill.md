---
name: security
description: Security best practices and OWASP compliance for Django applications. Use for any task involving authentication, authorization, data validation, or sensitive operations.
---

# Django Security Guidelines

**Always prioritize security:**

- Use Django’s built-in protections (CSRF, XSS, Clickjacking, etc.).
- Never use `mark_safe` unless you fully sanitize the content.
- Validate **all** user input (forms, serializers, API endpoints).
- Use proper permissions and role-based access.
- Store secrets in environment variables only.
- Hash sensitive data (use `django.contrib.auth.hashers`).
- Protect against common OWASP Top 10 risks.
- Use `HttpsOnly` and secure cookies in production.
- Rate-limit login attempts and sensitive endpoints.

**Authentication Rules:**
- Enforce strong password policies.
- Implement proper password reset flows with tokens.
- Use email verification for registrations when appropriate.

Flag any potential security issues immediately.