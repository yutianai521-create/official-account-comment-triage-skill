#!/usr/bin/env python3
"""Merge normalized official-account comments into a persistent JSON ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CLASSES = {"P0", "P1", "reply_optional", "no_action", "unreviewed"}
MATERIAL_FIELDS = (
    "body",
    "classification",
    "risk_reason",
    "recommended_action",
    "reply_draft",
    "resolution_status",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return " ".join(normalized.split()).strip().lower()


def text_hash(value: str) -> str:
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def make_key(item: dict[str, Any]) -> str:
    platform = str(item.get("platform", "")).strip().lower()
    post_id = str(item.get("parent_post_id", "")).strip()
    comment_id = str(item.get("comment_id", "")).strip()
    author_id = str(item.get("author_id", "")).strip()
    body = str(item.get("body", ""))
    if not platform or not post_id or not body.strip():
        raise ValueError("platform, parent_post_id, and non-empty body are required")
    if comment_id:
        return f"{platform}|{post_id}|{comment_id}"
    if not author_id:
        raise ValueError("author_id is required when comment_id is missing")
    return f"{platform}|{post_id}|{author_id}|{text_hash(body)}"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def validate_classification(value: Any) -> str:
    classification = str(value or "unreviewed")
    if classification not in CLASSES:
        raise ValueError(f"unsupported classification: {classification}")
    return classification


def build_record(item: dict[str, Any], seen_at: str) -> dict[str, Any]:
    record = dict(item)
    record["platform"] = str(item["platform"]).strip().lower()
    record["parent_post_id"] = str(item["parent_post_id"]).strip()
    record["comment_id"] = str(item.get("comment_id", "")).strip()
    record["author_id"] = str(item.get("author_id", "")).strip()
    record["author_name"] = str(item.get("author_name", "")).strip()
    record["body"] = str(item["body"])
    record["normalized_text_hash"] = text_hash(record["body"])
    record["comment_key"] = make_key(record)
    record["classification"] = validate_classification(item.get("classification"))
    record["is_official_author"] = bool(item.get("is_official_author", False))
    record["first_seen_at"] = str(item.get("first_seen_at") or seen_at)
    record["last_seen_at"] = seen_at
    record.setdefault("alerted_at", None)
    record.setdefault("reply_status", "not_replied")
    record.setdefault("resolution_status", "open")
    record.setdefault("last_card_date", None)
    return record


def is_materially_changed(old: dict[str, Any], new: dict[str, Any]) -> bool:
    return any(old.get(field) != new.get(field) for field in MATERIAL_FIELDS)


def merge(input_doc: dict[str, Any], ledger_doc: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    comments = input_doc.get("comments")
    if not isinstance(comments, list):
        raise ValueError("input JSON must contain a comments array")
    seen_at = str(input_doc.get("run_at") or now_iso())
    existing = ledger_doc.get("records", {})
    if not isinstance(existing, dict):
        raise ValueError("ledger records must be an object keyed by comment_key")

    delta: dict[str, list[dict[str, Any]]] = {
        "new": [],
        "changed": [],
        "unchanged": [],
        "official_excluded": [],
        "actionable": [],
    }
    records = dict(existing)

    for raw in comments:
        if not isinstance(raw, dict):
            raise ValueError("every comments item must be an object")
        incoming = build_record(raw, seen_at)
        key = incoming["comment_key"]
        old = records.get(key)
        if old is None:
            records[key] = incoming
            bucket = "new"
        else:
            incoming["first_seen_at"] = old.get("first_seen_at", incoming["first_seen_at"])
            for field in ("alerted_at", "reply_status", "resolution_status", "last_card_date"):
                if field not in raw:
                    incoming[field] = old.get(field, incoming.get(field))
            bucket = "changed" if is_materially_changed(old, incoming) else "unchanged"
            records[key] = {**old, **incoming}
        delta[bucket].append(records[key])

        if records[key].get("is_official_author"):
            delta["official_excluded"].append(records[key])

    delta["actionable"] = [
        record
        for record in records.values()
        if not record.get("is_official_author")
        and record.get("classification") in {"P0", "P1"}
        and record.get("resolution_status") != "resolved"
    ]
    new_ledger = {
        "schema_version": 1,
        "updated_at": seen_at,
        "records": dict(sorted(records.items())),
    }
    summary = {name: len(items) for name, items in delta.items()}
    return new_ledger, {"run_at": seen_at, "summary": summary, **delta}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    ingest = subparsers.add_parser("ingest", help="merge a comment batch into the ledger")
    ingest.add_argument("--input", type=Path, required=True)
    ingest.add_argument("--ledger", type=Path, required=True)
    ingest.add_argument("--output", type=Path, required=True, help="delta/audit JSON path")
    args = parser.parse_args()

    if args.command == "ingest":
        input_doc = read_json(args.input, {})
        ledger_doc = read_json(args.ledger, {"schema_version": 1, "records": {}})
        new_ledger, delta = merge(input_doc, ledger_doc)
        write_json_atomic(args.ledger, new_ledger)
        write_json_atomic(args.output, delta)
        print(json.dumps(delta["summary"], ensure_ascii=False, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
