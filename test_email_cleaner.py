import unittest

from email_cleaner import (
    clean_email,
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

    def test_invalid_email_is_not_disposable(self):
        disposable_domains = {
            "mailinator.com",
        }

        self.assertFalse(
            is_disposable_email(
                "invalid-email",
                disposable_domains
            )
        )

    def test_disposable_domain_case_insensitive(self):
        disposable_domains = {
            "mailinator.com",
        }

        self.assertTrue(
            is_disposable_email(
                "USER@MAILINATOR.COM",
                disposable_domains
            )
        )


if __name__ == "__main__":
    unittest.main()
