# Spec: Website Edit Permissions

## Problem Statement
Owners and staff need predictable edit access and lifecycle behavior without exposing non-public websites or returning misleading AJAX responses.

## User Stories
1. As a registered owner, I want to edit my website, so that its information stays current.
   - Acceptance criteria:
     - [ ] An unauthenticated edit request redirects to login with status 302.
     - [ ] An authenticated non-owner edit request redirects to the website detail page with status 302 and a Persian denial message.
     - [ ] An owner can edit their own non-deleted website.
     - [ ] Any owner edit of an approved website, including a no-op or minor edit, changes its status to `pending` and displays a Persian message that it is awaiting staff approval.
2. As staff, I want to edit any non-deleted website from its detail page, so that I can correct listing information.
   - Acceptance criteria:
     - [ ] Staff see the edit control on an accessible website detail page.
     - [ ] A staff edit through the owner-facing edit page follows the same approved-to-pending rule.
     - [ ] An edit performed in the staff dashboard does not implicitly change moderation status.
3. As a visitor, I want forbidden staff AJAX requests to return a clear authorization response.
   - Acceptance criteria:
     - [ ] A POST to any staff AJAX endpoint by an anonymous or non-staff user returns HTTP 403 JSON with `status="error"` and a Persian `message`.
     - [ ] Staff AJAX endpoints remain POST-only and CSRF-protected.

## In Scope / Out of Scope
- In scope: owner/staff access to website edits, lifecycle messages, and staff AJAX authorization responses.
- Out of scope: changing website status values, moderation policy, or staff-dashboard edit lifecycle.

## Assumptions / Open Questions
- The existing non-owner page experience remains a redirect to the website detail page (302).
- Staff AJAX uses HTTP 403 JSON rather than redirecting to an HTML login page; page requests continue to use normal login/redirect behavior.
- No open questions.

## Names introduced
| Kind | Name | Naming-law rule |
|---|---|---|
| Context key | `can_edit_website` | English `snake_case`; boolean capability uses `can_` |

## Revision Notes
- 2026-11-24: Aligned approved-site edits, page redirects, staff AJAX denial responses, and the staff detail-page edit control with the Phase 1.3 roadmap.