#!/usr/bin/env python3
"""Validate a brand profile for the official-account comment triage skill."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


BRAND_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
FORBIDDEN_KEY_PARTS = {"password", "cookie", "secret", "token", "api_key", "apikey"}


def walk_keys(value: Any, path: str = "") -> list[str]:
    violations: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            child_path = f"{path}.{key}" if path else str(key)
            if any(part in key_text for part in FORBIDDEN_KEY_PARTS):
                violations.append(child_path)
            violations.extend(walk_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            violations.extend(walk_keys(child, f"{path}[{index}]"))
    return violations


def validate(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    brand_id = config.get("brand_id")
    if not isinstance(brand_id, str) or not BRAND_ID.fullmatch(brand_id):
        errors.append("brand_id must be 2-64 lowercase letters, numbers, underscores, or hyphens")
    for field in ("brand_name", "report_language", "reply_language", "reply_tone"):
        if not isinstance(config.get(field), str) or not config[field].strip():
            errors.append(f"{field} must be a non-empty string")

    accounts = config.get("official_accounts")
    if not isinstance(accounts, dict) or not accounts:
        errors.append("official_accounts must be a non-empty object")
    else:
        normalized: set[tuple[str, str]] = set()
        for platform, identities in accounts.items():
            if not isinstance(platform, str) or not platform.strip():
                errors.append("official_accounts platform keys must be non-empty strings")
                continue
            if not isinstance(identities, list) or not identities:
                errors.append(f"official_accounts.{platform} must be a non-empty array")
                continue
            for identity in identities:
                if not isinstance(identity, str) or not identity.strip():
                    errors.append(f"official_accounts.{platform} contains an empty identity")
                    continue
                pair = (platform.strip().lower(), identity.strip().lower())
                if pair in normalized:
                    errors.append(f"duplicate official account: {platform}/{identity}")
                normalized.add(pair)

    forbidden = walk_keys(config)
    if forbidden:
        errors.append("configuration must not contain credentials: " + ", ".join(forbidden))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    args = parser.parse_args()
    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    if not isinstance(config, dict):
        print("configuration root must be an object")
        return 2
    errors = validate(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2
    print(f"valid brand profile: {config['brand_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
