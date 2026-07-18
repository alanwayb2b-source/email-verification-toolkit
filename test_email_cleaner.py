import unittest

from email_cleaner import clean_email, is_valid_email


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


if __name__ == "__main__":
    unittest.main()
