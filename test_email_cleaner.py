import unittest
from unittest.mock import patch

from email_cleaner import (
    clean_email,
    has_valid_mx,
    is_disposable_email,
    is_valid_email,
)


class TestEmailCleaner(unittest.TestCase):

    def test_clean_email(self):
        self.assertEqual(
            clean_email("  JOHN@EXAMPLE.COM  "),
            "john@example.com"
        )

    def test_valid_email(self):
        self.assertTrue(
            is_valid_email("john@example.com")
        )

    def test_invalid_email(self):
        self.assertFalse(
            is_valid_email("invalid-email")
        )

    def test_empty_email(self):
        self.assertFalse(
            is_valid_email("")
        )

    def test_disposable_email(self):
        disposable_domains = {
            "mailinator.com",
            "tempmail.com",
        }

        self.assertTrue(
            is_disposable_email(
                "user@mailinator.com",
                disposable_domains
            )
        )

    def test_normal_email_is_not_disposable(self):
        disposable_domains = {
            "mailinator.com",
            "tempmail.com",
        }

        self.assertFalse(
            is_disposable_email(
                "user@example.com",
                disposable_domains
            )
        )

    @patch("email_cleaner.dns.resolver.resolve")
    def test_valid_mx(self, mock_resolve):
        mock_resolve.return_value = ["mx1.example.com"]

        self.assertTrue(
            has_valid_mx("user@example.com")
        )

    @patch("email_cleaner.dns.resolver.resolve")
    def test_no_mx(self, mock_resolve):
        import dns.resolver

        mock_resolve.side_effect = dns.resolver.NoAnswer

        self.assertFalse(
            has_valid_mx("user@example.com")
        )

    @patch("email_cleaner.dns.resolver.resolve")
    def test_dns_timeout(self, mock_resolve):
        import dns.resolver

        mock_resolve.side_effect = dns.resolver.Timeout

        self.assertIsNone(
            has_valid_mx("user@example.com")
        )

    def test_invalid_email_mx(self):
        self.assertFalse(
            has_valid_mx("invalid-email")
        )


if __name__ == "__main__":
    unittest.main()
