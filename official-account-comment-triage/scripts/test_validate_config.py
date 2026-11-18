#!/usr/bin/env python3

import unittest

from validate_config import validate


def valid_config():
    return {
        "brand_id": "example_brand",
        "brand_name": "Example Brand",
        "report_language": "zh-CN",
        "reply_language": "match_comment",
        "reply_tone": "calm and helpful",
        "official_accounts": {"x": ["@example_brand"]},
    }


class ConfigTests(unittest.TestCase):
    def test_valid_profile(self):
        self.assertEqual(validate(valid_config()), [])

    def test_credentials_are_rejected(self):
        config = valid_config()
        config["api_token"] = "do-not-store-this"
        self.assertTrue(any("credentials" in item for item in validate(config)))

    def test_duplicate_accounts_are_rejected(self):
        config = valid_config()
        config["official_accounts"]["x"] = ["@Example_Brand", "@example_brand"]
        self.assertTrue(any("duplicate official account" in item for item in validate(config)))


if __name__ == "__main__":
    unittest.main()
