---
name: django-rest-framework
description: Best practices for building APIs with Django REST Framework. Use when creating serializers, viewsets, routers, authentication, or API endpoints.
---

# Django REST Framework Best Practices

**Core Principles:**
- Use `ModelSerializer` when possible, `Serializer` for complex/non-model data.
- Prefer **ViewSets + Routers** for standard CRUD.
- Use `GenericAPIView` + mixins only when you need fine control.
- Always define proper `permission_classes` and `authentication_classes`.

**Key Rules:**
- Use `serializers.PrimaryKeyRelatedField` or `HyperlinkedRelatedField` appropriately.
- Implement custom `validate()` methods for complex validation.
- Use `select_related()` / `prefetch_related()` in querysets.
- Return meaningful error messages.
- Version your APIs (e.g., `/api/v1/`).
- Document with drf-spectacular or drf-yasg.

**Pagination & Filtering:**
- Always enable pagination on list endpoints.
- Use `DjangoFilterBackend` or `SearchFilter` when needed.

**Authentication:**
- Prefer JWT (djangorestframework-simplejwt) or Token authentication based on project choice.
- Never expose sensitive data in responses.

Use this skill for any API-related task.