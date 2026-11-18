# Comment classification

Assign exactly one class after reading the full visible body and available context.

## P0 — urgent

Use when immediate escalation is warranted, including:

- account compromise, credential exposure, or credible security abuse;
- unexpected charges, payment loss, or serious billing harm;
- privacy or personal-data exposure;
- legal or regulatory threats with concrete facts;
- credible safety threats or a fast-growing public crisis.

P0 output must include the evidence, owner to notify, immediate containment action, and a cautious acknowledgement draft. Do not speculate or admit fault.

## P1 — official response required

Use for a concrete product or policy issue that needs investigation or explanation, including:

- reproducible product failure or blocked paid functionality;
- inconsistency between observed behavior and published policy;
- deletion, DeepRest, restricted-mode, data-handling, or entitlement disputes;
- a high-visibility negative claim with enough detail to verify;
- repeated unresolved support requests on the same issue.

P1 output must include why it needs handling, the evidence to verify, a suggested internal action, and a reply draft that asks only for safe identifiers through the proper support channel.

## reply_optional

Use for ordinary questions, constructive feedback, positive interaction, or a low-risk request that may benefit from a friendly response but does not require escalation.

## no_action

Use for praise, emojis, generic reactions, bounty/invite codes, unrelated promotions, obvious spam, or content with no concrete product, payment, security, privacy, or policy issue.

## Mandatory exclusions and safeguards

- Exclude the official account's own replies from user P0/P1 counts.
- A mention of “payment,” “privacy,” or another keyword alone is not enough; classify from meaning and context.
- Do not label criticism P0/P1 merely because it is negative.
- Do not downgrade a concrete complaint because the tone is polite.
- If the body is truncated or unavailable, classify as `unreviewed` in the audit rather than guessing; `unreviewed` is not a user-facing class.
- Preserve original language. When a translation is needed, provide an accurate complete translation and retain the original body.
