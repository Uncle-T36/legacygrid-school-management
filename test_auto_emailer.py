import unittest
from unittest.mock import patch, MagicMock
import auto_emailer

class TestAutoEmailer(unittest.TestCase):

    def setUp(self):
        self.smtp_cfg = {
            'server': 'smtp.test.com',
            'port': 587,
            'user': 'user@test.com',
            'password': 'password'
        }
        self.data = {
            "student_name": "Jane Doe",
            "parent_name": "John Doe",
            "amount": "500",
            "date": "2025-09-15"
        }
        self.to_email = "parent@email.com"
        self.from_email = "school@email.com"

    @patch("auto_emailer.smtplib.SMTP")
    @patch("auto_emailer.os.path.exists", return_value=True)
    @patch("auto_emailer.load_template")
    def test_send_event_email_success(self, mock_load_template, mock_exists, mock_smtp):
        mock_template = MagicMock()
        mock_template.safe_substitute.return_value = "Subject: Payment Received\nBody text"
        mock_load_template.return_value = mock_template

        result = auto_emailer.send_event_email(
            "payment_received",
            self.data,
            self.to_email,
            self.from_email,
            self.smtp_cfg
        )

        self.assertTrue(result)
        mock_smtp.assert_called_with(self.smtp_cfg['server'], self.smtp_cfg['port'])
        mock_template.safe_substitute.assert_called_with(self.data)

    @patch("auto_emailer.os.path.exists", return_value=False)
    def test_send_event_email_missing_template(self, mock_exists):
        result = auto_emailer.send_event_email(
            "unknown_event",
            self.data,
            self.to_email,
            self.from_email,
            self.smtp_cfg
        )
        self.assertFalse(result)

    @patch("auto_emailer.smtplib.SMTP", side_effect=Exception("SMTP failure"))
    @patch("auto_emailer.os.path.exists", return_value=True)
    @patch("auto_emailer.load_template")
    def test_send_event_email_smtp_failure(self, mock_load_template, mock_exists, mock_smtp):
        mock_template = MagicMock()
        mock_template.safe_substitute.return_value = "Subject: Payment Received\nBody text"
        mock_load_template.return_value = mock_template

        result = auto_emailer.send_event_email(
            "payment_received",
            self.data,
            self.to_email,
            self.from_email,
            self.smtp_cfg
        )
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()