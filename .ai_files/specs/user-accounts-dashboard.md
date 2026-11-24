# Spec: User Accounts & Dashboard

## Problem Statement
Users register/login and manage their submissions and reviews.

## User Stories
1. As a visitor, I want register/login/logout.
2. As a user, I want a dashboard of my websites and reviews.
3. As an owner, I want to edit my website and know whether it needs re-approval.

## In Scope
- Auth views, `user_dashboard`, `edit_website`, delete own site/review

## Out of Scope
- OAuth/SSO
- Public profiles (Phase 3)

## Assumptions
- Any edit of an approved website through the owner-facing edit page → `pending` again. Staff dashboard edits preserve the current moderation status.
