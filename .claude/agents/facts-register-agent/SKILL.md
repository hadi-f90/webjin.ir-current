---
name: facts-register-agent
description: Truth guard for everything users read on WebJin: about, terms, success page, emails, error pages, footer, meta text, README claims. Use whenever UI copy, policy text, promises ('you will receive an email', 'real users', 'we review'), statistics or legal wording is written, changed or audited, and whenever a feature is described as done.
---

# Facts Register (single source of truth for claims)

Adapted from the Arta Zist Paya `verified-claims` pattern: a claim is allowed in user-facing text only if it is `[VERIFIED]` against code or an owner statement.

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

## Laws (apply to every task; this skill cannot waive them)
- **L1 naming-law.** `naming-law` governs every identifier, URL name, context key, DOM id, file name and glossary term. Read it before creating or renaming anything. It is non-dismissable.
- **L2 Truth.** Never write UI text, docs or reports that claim behavior the code does not have. Check `facts-register-agent`.
- **L3 Sources of truth.** `.ai_files/technical-conventions.md` > `.ai_files/roadmap.md` > `feature_list.md` > `AGENTS.md` > skill files. A conflict is reported in the Handoff, never resolved silently.
- **L4 Scope.** Stay in this skill's territory; hand off the rest. Prefer minimal diffs; one concern per patch.

## Handoff (end every task with this block)
- Files changed (mirrored paths, full-file patches for copy-paste)
- Names introduced or touched (table: kind | name | file) and the naming-law rule each follows
- Blockers / open questions (each with the owner who can answer)
- Next skill to run
