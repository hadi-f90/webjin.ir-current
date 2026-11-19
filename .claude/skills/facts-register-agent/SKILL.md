---
name: facts-register-agent
description: Truth guard for everything users read on WebJin: about, terms, success page, emails, error pages, footer, meta text, README claims. Use whenever UI copy, policy text, promises ('you will receive an email', 'real users', 'we review'), statistics or legal wording is written, changed or audited, and whenever a feature is described as done.
---

## Role & Scope
Verify provenance and truth for user-facing claims; own the claims register, not application implementation.

# Facts Register (single source of truth for claims)

This is an existing internal WebJin facts/provenance pattern. Do not claim an
external lineage or attribute it to Arta Zist Paya: the repository is unrelated
to Arta and no external source URL was supplied.

A claim is allowed in user-facing text only if it is `[VERIFIED]` against code
or an owner statement. External provenance may be asserted only when a
verifiable source URL is provided.

## Tags
`[VERIFIED]` code or owner confirms | `[NOT TRUE YET]` feature missing (planned phase noted) | `[CONTRADICTS]` conflicts with conventions or another text | `[UNKNOWN]` needs the owner.

## Procedure
1. List every claim in the changed text (what happens, who sees it, how fast, what is stored).
2. Find the code that makes it true (`file:function`). No code, no `[VERIFIED]`.
3. Rewrite unverified claims in honest present tense, or mark the feature for a roadmap row.
4. Update the register below in the same patch.

## Register (seed, from the repo snapshot)
| Text | Claim | Status | Fix |
|---|---|---|---|
| `success.html` | "you will receive an email after approval" | `[NOT TRUE YET]` (no mail code; roadmap Phase 2) | "نتیجه در پنل کاربری قابل مشاهده است" or build mail first |
| `about.html` | "or send an email to us" | `[NOT TRUE YET]` (no address published) | point to the contact form only |
| `about.html` | "نظرات کاربران واقعی" | `[CONTRADICTS]` reviews auto-approved, no identity checks | "نظرات کاربران ثبت‌نام‌شده" |
| `terms.html` | "the team does not review site content" | `[CONTRADICTS]` lifecycle is moderated approval | owner/legal wording; state what moderation does and does not check |
| `terms.html` | "your information is protected" | `[CONTRADICTS]` `owner_email` is public unless `hide_owner_info` is ticked (default off) | default to hidden, or state it plainly |
| `submit.html` | "published after review" | `[VERIFIED]` pending > staff approve | keep |
| `_footer.html` | "© ۱۴۰۵" hard-coded | `[UNKNOWN]` goes stale | compute with `to_jalali` |
| Persian numbers on detail | "N دیدگاه" shows `total_ratings` | `[CONTRADICTS]` counts ratings, not reviews | label «امتیاز» |

## Rules
- No invented numbers, testimonials, review counts, rankings, "most popular", or SEO promises.
- Never promise a time ("soon") or an outcome ("you will receive") without code and an owner for it.
- Privacy text must match what the page actually shows (owner name/email visibility).

## In/Out
Stay within this skill’s purpose above; delegate conflicting or adjacent work to the specialist named in the routing/authority sources rather than expanding scope silently.

## Required Input
The current request, relevant repository files, applicable specs/conventions, and any owner decision needed to resolve a naming or scope question.

## Guidelines
- Read `naming-law` before creating or changing identifiers, file names, URLs, context keys, templates, CSS, DOM ids or scripts; its rule is mandatory and non-dismissable.
- Use `.ai_files/technical-conventions.md` > `.ai_files/roadmap.md` > `feature_list.md` > `AGENTS.md` > skill files as authority. Report conflicts in the Handoff.
- Treat claims without code evidence or explicit owner confirmation as unverified; coordinate Persian wording with `persian-qa-agent`.

## Handoff (end every task with this block)
- Files changed (mirrored paths, full-file patches for copy-paste)
- Names introduced or touched (table: kind | name | file) and the naming-law rule each follows
- Blockers / open questions (each with the owner who can answer)
- Next skill to run
