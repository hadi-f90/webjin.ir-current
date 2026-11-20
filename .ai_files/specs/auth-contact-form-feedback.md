# Spec: Authentication and Contact Form UX

## Problem Statement
The signup, login, and contact forms do not share the clear RTL field presentation used by website submission, and their current server-rendered responses do not provide consistent, accessible AJAX feedback. Visitors need understandable validation and confirmation while all forms continue to work without JavaScript.

## User Stories
1. As a visitor, I want signup and login fields to be clearly labeled and consistently laid out, so that I can create an account or sign in without confusion.
   - Acceptance criteria:
     - [ ] Signup presents username, password, and repeat-password as separate, labeled controls; login presents username and password as separate, labeled controls.
     - [ ] Both pages use the website-submission page's clear RTL form conventions: readable field labels, consistent control sizing and spacing, and an easy-to-find submit action.
     - [ ] Field validation errors are shown beside the relevant field; form-level errors (such as invalid credentials) are shown in a visible summary.
2. As a visitor, I want the contact form to use the same clear field presentation and receive confirmation or correction guidance, so that I know whether my message was sent.
   - Acceptance criteria:
     - [ ] Contact fields retain their existing purpose and validation and are presented with clear labels, consistent spacing, and readable field-level errors in the site's RTL form style.
     - [ ] A valid submission is saved once and produces a visible success confirmation.
     - [ ] An invalid submission preserves non-sensitive entered values and shows errors beside the relevant fields, including captcha validation when applicable.
3. As a visitor submitting any of these forms with JavaScript enabled, I want clear feedback without losing the form context on validation failure, so that I can correct and resubmit it.
   - Acceptance criteria:
     - [ ] Signup, login, and contact submissions use AJAX as an enhancement to their existing POST forms; a validation failure stays on the form, preserves applicable values, displays field and form errors, and restores the submit button.
     - [ ] AJAX responses reuse the existing public submission response convention: `status` and `message`, optional `redirect` on success, and optional field-keyed `errors` on failure. Validation errors use the existing field-to-message-list shape.
     - [ ] Successful signup and login retain their existing destination (the index); contact retains its existing contact-page destination. The success message is available to the user on the destination page. No new endpoint or response contract is introduced.
     - [ ] Network failures, non-JSON responses, and unexpected server errors produce a plain-language retry message, do not report success, and restore the submit control.
4. As a visitor using assistive technology or keyboard navigation, I want form feedback to be announced and connected to its field, so that I can complete the form independently.
   - Acceptance criteria:
     - [ ] Inputs have programmatically associated labels; field errors are associated with their inputs and invalid controls expose their invalid state.
     - [ ] An error summary and success/error feedback are announced through appropriate live-region semantics; errors are not communicated by color alone.
     - [ ] After an AJAX validation failure, focus moves to the error summary or first invalid field, and all controls and feedback remain keyboard accessible.
5. As a visitor without JavaScript, I want to submit each form through its normal POST flow, so that these pages remain usable when scripting is unavailable.
   - Acceptance criteria:
     - [ ] Signup, login, and contact continue to render and process ordinary POST requests using their existing server-side validation and success destinations.
     - [ ] Invalid ordinary POST requests rerender the relevant form with server-side errors; successful requests keep the current account and contact behavior while making success feedback visible.

## In Scope
- Field layout and feedback on signup, login, and contact pages, following the RTL form conventions visible on the website-submission page.
- Accessible inline field errors, form-level errors, AJAX progress/error/success feedback, and progressive enhancement.
- Updating the existing signup/login views and contact form view only as needed to negotiate AJAX requests and return feedback in the established public-submission response shape.
- Making contact success feedback visible; the current `success_message` is not currently passed to the response.

## Out of Scope
- Changing authentication rules, account fields, password policy, contact fields, captcha policy, storage, or spam handling.
- New endpoints, authentication providers, models, or API response formats.
- Changes to website submission or staff moderation behavior.
- Redesigning unrelated site pages or shared site chrome.

## Assumptions
- Website submission (`directory/views.py`) is the reference for the existing public AJAX response shape; staff-only AJAX conventions are not being broadened.
- Successful signup and login continue to redirect to the index; successful contact submission continues to return to the contact page.
- The same server-side Django forms remain authoritative for validation. AJAX mirrors their errors rather than replacing them with client-only validation.
- The shared visual language remains Persian-first and RTL; the request does not require identical page content or fields.

## Open Questions
- None blocking. Backend implementation must verify that the AJAX response carries the current success destinations and that the contact success message is visible after the existing redirect.
