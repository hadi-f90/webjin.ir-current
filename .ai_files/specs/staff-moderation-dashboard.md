# Spec: Staff Moderation Dashboard

## Problem Statement
Staff need a single dashboard to approve, reject, edit, and manage categories/tags/reports via AJAX without full page reloads.

## User Stories
1. As staff, I want to list pending websites and approve/reject/delete them via AJAX.
   - Acceptance criteria:
     - [ ] Non-staff get redirect (302) away from dashboard
     - [ ] Staff see pending titles
     - [ ] AJAX endpoints return `{status, message, ...}` JSON
2. As staff, I want edit/status modals to use matching DOM IDs and CSRF headers.
3. As staff, I want accurate pending and report counts.

## In Scope
- Existing AJAX endpoints under `directory/urls.py`
- Modal ID consistency (`editWebsiteModal`)
- CSRF on all POST AJAX

## Out of Scope
- Full Django admin replacement
- Bulk import UI (Phase 2+)

## Assumptions
- `staff_member_required` / `user_passes_test(is_admin)` gating

## Open Questions
- Soft-delete vs rejected-reason field (product decision still open on roadmap)
