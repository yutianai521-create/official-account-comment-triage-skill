# Daily report and alert rendering

## Daily card comment section

Show only actionable P0/P1 comments. Each displayed item must contain:

- priority, platform, and author;
- full original body, or an accurate complete translation plus original body;
- concise risk/issue assessment;
- recommended owner/action;
- ready-to-review reply draft;
- direct comment link.

Do not display the bodies of `reply_optional` or `no_action` comments. Summarize them only as counts, for example: “另核验 12 条普通评论，无需处理。”

If every accessible comment is reviewed and there is no P0/P1, use:

```text
今日未发现需要官方处理的 P0/P1 评论。
```

If coverage is incomplete, do not use that sentence without qualification. State which platforms remain unreviewed in one concise line.

## Repeat suppression

An unchanged unresolved P0/P1 already shown on a prior card should not be repeated in full. Use:

```text
存量 P1：@author 的 [issue] 待处理，昨日已提醒，本日无变化。
```

Display it in full again only when the body, risk, recommended action, or resolution state changes.

## Separate alert

Create a separate alert only for a newly verified P0/P1 or a material escalation. Do not send alerts for counts without bodies, ordinary criticism, praise, spam, bounty codes, or official-account replies.

No automated external send or public reply is authorized by this skill. Return the alert payload to the calling workflow for its own delivery and approval controls.
