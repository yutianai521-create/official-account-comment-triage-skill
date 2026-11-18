# Unified schema

## Input

`comment_ledger.py ingest` accepts a JSON object:

```json
{
  "run_at": "2026-11-18T12:15:00+08:00",
  "comments": [
    {
      "platform": "x",
      "parent_post_id": "2122700241426391329",
      "comment_id": "212271843135266985",
      "author_id": "SandraLMur",
      "author_name": "Sandra",
      "body": "Full visible comment body",
      "comment_url": "https://x.com/...",
      "published_at": "2026-11-18T10:00:00+08:00",
      "is_official_author": false,
      "classification": "P1",
      "risk_reason": "Concrete policy discrepancy",
      "recommended_action": "Verify account state and policy scope",
      "reply_draft": "Thanks for flagging this..."
    }
  ]
}
```

Fields through `body` are required. `comment_id` is preferred; without it, `author_id` is required. Classification fields may be added before or after model review.

## Ledger record

Each stored record contains:

- `comment_key`
- `platform`
- `parent_post_id`
- `comment_id`
- `author_id`, `author_name`
- `body`, `normalized_text_hash`
- `comment_url`, `published_at`
- `is_official_author`
- `first_seen_at`, `last_seen_at`
- `classification`, `risk_reason`
- `recommended_action`, `reply_draft`
- `alerted_at`, `reply_status`, `resolution_status`, `last_card_date`

Allowed classifications are `P0`, `P1`, `reply_optional`, `no_action`, and internal-only `unreviewed`.

## Identity

When `comment_id` exists:

```text
platform|parent_post_id|comment_id
```

Otherwise:

```text
platform|parent_post_id|author_id|sha256(normalized_body)
```

Normalization applies Unicode NFKC, trims ends, collapses whitespace, and lowercases. The script hashes normalized text without discarding the original body.

## Delta output

The script writes:

- `new`: unseen keys;
- `changed`: known keys whose body or material classification fields changed;
- `unchanged`: known keys seen again without material change;
- `official_excluded`: official-account replies stored for audit but excluded from risk counts;
- `actionable`: current non-official P0/P1 records that have not been resolved.

The ledger file is replaced atomically only after validation succeeds.
