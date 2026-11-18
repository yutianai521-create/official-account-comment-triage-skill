#!/usr/bin/env python3

import unittest

from comment_ledger import make_key, merge, normalize_text


class CommentLedgerTests(unittest.TestCase):
    def test_normalization_and_fallback_key_are_stable(self):
        left = {
            "brand_id": "example_brand",
            "platform": "X",
            "parent_post_id": "post-1",
            "author_id": "user-1",
            "body": "  Hello\u3000WORLD  ",
        }
        right = {**left, "body": "hello world"}
        self.assertEqual(normalize_text(left["body"]), "hello world")
        self.assertEqual(make_key(left), make_key(right))

    def test_incremental_merge_and_official_exclusion(self):
        first = {
            "brand_id": "example_brand",
            "run_at": "2026-11-18T12:15:00+08:00",
            "comments": [
                {
                    "platform": "x",
                    "parent_post_id": "post-1",
                    "comment_id": "comment-1",
                    "author_id": "user-1",
                    "body": "My paid subscription stopped working unexpectedly.",
                    "classification": "P1",
                },
                {
                    "platform": "x",
                    "parent_post_id": "post-1",
                    "comment_id": "comment-2",
                    "author_id": "example_brand_official",
                    "body": "We are checking this.",
                    "classification": "reply_optional",
                    "is_official_author": True,
                },
            ],
        }
        ledger, delta = merge(first, {"schema_version": 1, "records": {}})
        self.assertEqual(delta["summary"]["new"], 2)
        self.assertEqual(delta["summary"]["actionable"], 1)
        self.assertEqual(delta["summary"]["official_excluded"], 1)

        second = {**first, "run_at": "2026-11-19T12:15:00+08:00"}
        _, repeat = merge(second, ledger)
        self.assertEqual(repeat["summary"]["unchanged"], 2)
        self.assertEqual(repeat["summary"]["changed"], 0)
        self.assertEqual(repeat["summary"]["actionable"], 1)

    def test_material_change_is_detected(self):
        base = {
            "brand_id": "example_brand",
            "run_at": "2026-11-18T12:15:00+08:00",
            "comments": [
                {
                    "platform": "facebook",
                    "parent_post_id": "post-2",
                    "comment_id": "comment-3",
                    "author_id": "user-2",
                    "body": "It does not work.",
                    "classification": "unreviewed",
                }
            ],
        }
        ledger, _ = merge(base, {"records": {}})
        base["comments"][0]["classification"] = "P1"
        _, delta = merge(base, ledger)
        self.assertEqual(delta["summary"]["changed"], 1)

    def test_cross_brand_ledger_is_rejected(self):
        batch = {
            "brand_id": "brand_a",
            "comments": [
                {
                    "platform": "youtube",
                    "parent_post_id": "post-3",
                    "comment_id": "comment-4",
                    "author_id": "user-3",
                    "body": "A comment",
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "ledger brand_id"):
            merge(batch, {"brand_id": "brand_b", "records": {}})


if __name__ == "__main__":
    unittest.main()
