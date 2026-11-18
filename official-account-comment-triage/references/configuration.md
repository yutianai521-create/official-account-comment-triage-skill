# Brand profile configuration

Copy `config.example.json` to a task-owned configuration location and replace all example values. Do not commit credentials, cookies, tokens, workbook IDs, or private user data.

## Required fields

- `brand_id`: stable lowercase namespace used in ledger keys and audit paths.
- `brand_name`: display name.
- `official_accounts`: allowlisted identities by platform. A collector must fail closed for an identity not in this map.
- `report_language`: language for summaries.
- `reply_language`: `match_comment` or a fixed locale.
- `reply_tone`: short style instruction for drafts.

## Optional policy fields

- `included_account_types`: limits scope to global, regional, campaign, or other declared account types.
- `products`: vocabulary used to understand context, never as an automatic risk trigger.
- `priority_overrides`: brand-approved examples that refine, but do not weaken, the base P0/P1 policy.
- `no_action_patterns`: known low-value patterns. Match meaning, not raw keywords alone.
- `escalation_owners`: internal owner labels by risk domain.

## Multi-brand operation

Use one configuration and one ledger namespace per brand. Never merge records from different `brand_id` values into one ingestion batch. A shared deployment may reuse the same code, but must keep brand configuration, audits, ledgers, delivery state, and credentials isolated.

## Platform extension

Any additional platform may be used if its collector produces the unified schema. The core workflow must not contain platform-specific field aliases beyond the adapter boundary.
