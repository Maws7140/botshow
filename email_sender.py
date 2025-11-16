"""
Email sending module for the automated messaging bot.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import time


class EmailSender:
    """Handles sending emails to contacts."""

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_email: str, subject: str, body: str,
                   contact_name: str = '') -> bool:
        """
        Send an email to the specified recipient.

        Args:
            recipient_email: Recipient's email address
            subject: Email subject
            body: Email body content
            contact_name: Optional contact name for personalization

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email

            # Personalize body if name is provided
            personalized_body = body
            if contact_name:
                personalized_body = f"Dear {contact_name},\n\n{body}"

            # Add plain text version
            text_part = MIMEText(personalized_body, 'plain')
            message.attach(text_part)

            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            print(f"✓ Email sent successfully to {recipient_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print(f"✗ Authentication failed. Check email credentials.")
            return False
        except smtplib.SMTPException as e:
            print(f"✗ SMTP error occurred: {e}")
            return False
        except Exception as e:
            print(f"✗ Failed to send email to {recipient_email}: {e}")
            return False

    def test_connection(self) -> bool:
        """Test the SMTP connection."""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            print("✓ Email connection test successful")
            return True
        except Exception as e:
            print(f"✗ Email connection test failed: {e}")
            return False
