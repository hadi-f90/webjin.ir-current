# Spec: Website Trash

## Problem Statement
Owners and staff need to remove websites from public discovery without permanently deleting records, while retaining a reason and the identity of the person who moved each website to trash.

## User Stories
1. As an owner or staff member, I want to move a website to trash with an optional reason, so that it disappears from public pages without losing its record.
   - Acceptance criteria:
     - [ ] Owner and staff delete actions are POST-only and CSRF-protected.
     - [ ] Deletion sets `is_deleted`, `deleted_at`, `deleted_by`, and the trimmed optional `deletion_reason`; it does not change `pending`, `approved`, or `rejected` status.
     - [ ] Staff can move any non-deleted website to trash; an owner can move only their own.
     - [ ] Django admin cannot permanently delete websites or directly alter trash metadata; use the staff dashboard for trash actions.
     - [ ] Public index, category/tag counts, website search results, website details, and related-site results exclude trashed websites.
     - [ ] A public visitor receives 404 for a trashed website detail page.
2. As staff, I want a trash section in the staff dashboard, so that I can review deleted records and restore them when appropriate.
   - Acceptance criteria:
     - [ ] The staff trash section displays each trashed website, its deletion reason, and the deleting account when present.
     - [ ] Staff can restore any trashed website; restore clears `is_deleted` and preserves its moderation status.
3. As an owner, I want to see my trashed websites and deletion reasons, so that I know why a listing is unavailable.
   - Acceptance criteria:
     - [ ] The owner dashboard displays the owner's trashed websites, reason, and deleting account when present.
     - [ ] An owner can restore a website only when that owner moved it to trash.
     - [ ] An owner cannot restore a website moved to trash by staff.
     - [ ] The owner and staff can view a trashed detail page and its deletion reason; other visitors cannot.
     - [ ] After owner deletion, the dashboard says `وب‌سایت از فهرست اصلی شما حذف شد.` without claiming permanent erasure.

## In Scope / Out of Scope
- In scope: reversible website deletion, actor/time/reason metadata, owner and staff trash views, restore permissions, and excluding trash from public discovery.
- Out of scope: hard deletion, a separate deletion-history table, rejection reasons, changing moderation status values, or allowing owners to restore a staff-deleted website.

## Assumptions / Open Questions
- A single set of deletion metadata describes the latest deletion; restoring a website preserves that metadata until its next deletion.
- “Admin” means a Django staff user in the existing dashboard permission model.
- No open questions.

## Names introduced
| Kind | Name | Naming-law rule |
|---|---|---|
| Model field | `is_deleted` | English `snake_case`; boolean uses `is_` |
| Model field | `deleted_at` | English `snake_case`; timestamp uses `_at` |
| Model field | `deleted_by` | English `snake_case`; singular actor relation |
| Model field | `deletion_reason` | English `snake_case`; descriptive field |
| Reverse relation | `deleted_websites` | English plural `snake_case` noun |
| View | `restore_website_ajax` | English action name ending `_ajax`; staff AJAX path under `/ajax/` |
| View | `restore_my_website` | English action name in `snake_case` |

## Revision Notes
- 2026-11-24: Owner decision: use soft deletion with an optional reason; staff can restore any record, while an owner can restore only a record that owner deleted. Record the deleting user.
- 2026-11-24: Owner-facing confirmation uses concise, accurate wording that describes removal from the main list without exposing implementation terminology or claiming permanent erasure.