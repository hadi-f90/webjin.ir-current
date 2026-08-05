# Spec: Ratings & Reviews

## Problem Statement
Registered users rate (1–5) and review approved websites; aggregates update on the listing.

## User Stories
1. As a logged-in user, I want to POST a rating so my score is stored once per site (`update_or_create`).
2. As a logged-in user, I want to submit a review text shown when approved.

## In Scope
- `rate_website`, `review_website`, Rating/Review models
- `update_rating()` on Website

## Out of Scope
- Anonymous ratings
- Paid ranking by stars

## Assumptions
- Reviews default `is_approved=True` until a moderation queue is productized

## Open Questions
- Enforce one review per user?
