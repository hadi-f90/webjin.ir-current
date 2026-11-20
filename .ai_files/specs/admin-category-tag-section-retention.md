# Spec: Preserve Admin Category and Tag Section

## Problem Statement
Staff who add a category or tag from its dashboard section are returned to the general overview after the page reloads, interrupting their work. Category and tag create/edit actions should leave staff in the relevant dashboard section and clearly surface success or failure there.

## User Stories
1. As staff, I want to remain in the Categories section after adding or editing a category, so that I can continue managing categories without navigating back.
   - Acceptance criteria:
     - [ ] After a successful category add or edit, the dashboard remains on the Categories section.
     - [ ] After a successful add, the new category is visible in the refreshed list; after an edit, the updated category details are visible.
     - [ ] If the request fails validation or encounters a server/network error, the dashboard remains on the Categories section, displays an error, and preserves entered values so I can correct or retry.
2. As staff, I want to remain in the Tags section after adding or editing a tag, so that I can continue managing tags without navigating back.
   - Acceptance criteria:
     - [ ] After a successful tag add or edit, the dashboard remains on the Tags section.
     - [ ] After a successful add, the new tag is visible in the refreshed list; after an edit, the updated tag name is visible.
     - [ ] If the request fails validation or encounters a server/network error, the dashboard remains on the Tags section, displays an error, and preserves entered values so I can correct or retry.
3. As staff, I want success and validation feedback for category/tag changes to be understandable in the current section.
   - Acceptance criteria:
     - [ ] Successful create/edit actions show the existing success feedback without sending staff to the overview.
     - [ ] Empty-name and server-side validation failures are reported as errors rather than being presented as successful changes.
     - [ ] Failed requests leave the relevant section usable for another attempt.

## In Scope
- Preserve the active Categories or Tags dashboard section across successful add and edit actions.
- Keep category/tag validation and request failures in the relevant section, with clear feedback and retryable form state.
- Keep the dashboard data shown after a successful add/edit consistent with the server response.
- Regression coverage for category and tag add/edit success and failure section retention.

## Out of Scope
- Navigation behavior for website, report, user, review, delete, or other dashboard actions.
- Changes to category/tag CRUD rules, permissions, endpoints, or data fields.
- Redesign of the dashboard, modals, or general AJAX infrastructure beyond what is needed for this behavior.

## Assumptions
- “Same section” means the dashboard’s Categories section after category actions and Tags section after tag actions; it does not mean returning to the general overview.
- Existing staff access rules and the current JSON-based category/tag endpoints remain in effect.
- The Persian-first, RTL dashboard and its current success/error feedback conventions are retained.

## Open Questions
- None.

## Revision Notes (if applicable)
- Initial focused spec based on the current dashboard templates, category/tag views, routes, and tests.
