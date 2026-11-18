---
name: official-account-comment-triage
description: "Collect, audit, deduplicate, classify, and summarize comments on a brand's official-account posts across major social platforms. Use for daily official-account comment checks, configurable P0/P1 screening, incremental comment-ledger updates, actionable reply drafts, and comment sections in social reports. Supports TikTok, Instagram, YouTube, Facebook, X, and compatible normalized inputs. Do not use for broad keyword-based social listening, post-metric collection, or automatically publishing replies."
---

# Official Account Comment Triage

## Goal

Produce an evidence-backed, incremental review of comments on confirmed official posts. Preserve every visible comment in the internal ledger, but expose only comments that require official handling.

## Boundaries

- Read the brand profile before collection. Use `config.example.json` and `references/configuration.md` as the contract.
- Cover only accounts explicitly listed in `official_accounts`; reject records from unlisted accounts.
- Treat creator, employee, franchise, regional, matrix, and campaign accounts as out of scope unless the profile explicitly includes them.
- Do not replace the post-discovery or metric-collection workflow. Accept confirmed canonical post URLs and IDs as input.
- Do not reply, delete, hide, like, or report a comment without explicit authorization.
- Do not bypass CAPTCHAs, sliders, login challenges, or platform access controls. Switch to another legitimate logged-in or public path and record the limitation.
- Exclude replies authored by the official account from user-risk classification.

## Required inputs

For every platform, obtain or receive:

- `brand_id`
- `platform`
- `official_account_id`
- `parent_post_id`
- `canonical_post_url`
- the platform-reported comment/reply count when visible
- visible comment records, including author, body, comment ID or direct link, and timestamp when exposed
- the existing persistent ledger, if one exists

If the platform explicitly shows zero comments, record complete zero-comment coverage. If a count is nonzero but bodies are unavailable, mark the platform `partial`; never infer “no action needed” from the count alone.

## Workflow

1. Validate that each parent post is the confirmed latest official post supplied by the caller. Do not silently substitute an older post.
2. Validate the brand profile with `python scripts/validate_config.py <config.json>`, then validate the account against its allowlist. Fail closed when no valid profile is supplied or the account is not allowlisted.
3. Collect comments independently per platform. One platform failure must not block the others.
4. Save raw evidence or a lossless extraction before classification. Record the route used and any access limitation.
5. Normalize and merge records with `scripts/comment_ledger.py`. Use platform comment IDs when available; otherwise use the deterministic fallback key described in `references/schema.md`.
6. Review only new or materially changed records. Do not fully re-analyze unchanged ledger entries.
7. Classify with the base rules in `references/classification.md`, then apply the profile's `priority_overrides`, exclusions, product vocabulary, and escalation owners. Assign exactly one of `P0`, `P1`, `reply_optional`, or `no_action`.
8. For every P0/P1, preserve the full original body, author, direct comment link, rationale, recommended action, and a ready-to-review reply draft in the configured language and tone.
9. Render the user-facing section according to `references/reporting.md`: show P0/P1 only; summarize all other comments by count.
10. Persist the updated ledger and a run audit under the configured brand namespace. Report each platform as `complete`, `partial`, or `failed`.

## Incremental rules

- Primary identity: `brand_id + platform + parent_post_id + comment_id`.
- Fallback identity: `brand_id + platform + parent_post_id + author_id + normalized_text_hash`.
- Same post and same comment IDs: update `last_seen_at`; do not repeat analysis or alerts.
- Same post with additional IDs: process only the new comments.
- New parent post: perform a full comment check for that post.
- Previously alerted P0/P1 with unchanged text: do not repeat the full alert. Show only a compact unresolved-item note when still open.
- Re-open or re-alert only when the body, classification, risk, or resolution state materially changes.

## Quality gates

Before calling a platform complete, confirm one of:

- the page explicitly shows zero comments; or
- the visible comment records reconcile with the platform count; or
- pagination/end-of-list evidence proves all accessible comments were read.

The run is valid when at least one platform completes or partially completes and every platform has an honest status. A failed platform never cancels successful platform results.

## Output contract

Return:

- per-platform comment count, visible-body count, and coverage status;
- new, changed, unchanged, and resolved ledger counts;
- P0/P1 items with evidence and reply drafts;
- an explicit statement when no verified P0/P1 exists;
- paths or identifiers for the raw audit and updated ledger.

Keep technical collection diagnostics out of the user-facing daily card. Never claim “no P0/P1” for a platform whose nonzero comments were not actually read.
