import unittest
from unittest.mock import patch, MagicMock
import smtplib

from api.services.email import send_magic_link_email


class TestMailSender(unittest.TestCase):

    @patch("api.services.email.GMAIL_USER", "fake_user@gmail.com")
    @patch("api.services.email.GMAIL_APP_PASSWORD", "fake_password")
    @patch("api.services.email.smtplib.SMTP")
    def test_send_email_success(self, mock_smtp):
        """Prueba que el email se envía correctamente."""

        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        result = send_magic_link_email("test@example.com", "http://magic.link")

        self.assertTrue(result)

        mock_smtp.assert_called_with("smtp.gmail.com", 587)

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_with("fake_user@gmail.com", "fake_password")
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch("api.services.email.GMAIL_USER", None)
    @patch("api.services.email.GMAIL_APP_PASSWORD", None)
    @patch("api.services.email.smtplib.SMTP")
    def test_missing_credentials(self, mock_smtp):
        """Prueba que la función retorna False si faltan credenciales."""

        result = send_magic_link_email("test@example.com", "http://magic.link")

        self.assertFalse(result)

        mock_smtp.assert_not_called()

    @patch("api.services.email.GMAIL_USER", "fake_user@gmail.com")
    @patch("api.services.email.GMAIL_APP_PASSWORD", "fake_password")
    @patch("api.services.email.smtplib.SMTP")
    def test_send_email_failure(self, mock_smtp):
        """Prueba que la función retorna False si smtplib da una excepción."""

        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        mock_server.login.side_effect = smtplib.SMTPException("Error de autenticación")

        result = send_magic_link_email("test@example.com", "http://magic.link")

        self.assertFalse(result)

        mock_smtp.assert_called_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()

        mock_server.send_message.assert_not_called()
        mock_server.quit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
