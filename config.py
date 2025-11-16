"""
Configuration module for the automated messaging bot.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for bot settings."""

    # Email settings
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', '')

    # Marketplace settings
    MARKETPLACE_URL = os.getenv('MARKETPLACE_URL', '')

    # Message settings
    MESSAGE_SUBJECT = os.getenv('MESSAGE_SUBJECT', 'Business Opportunity')
    MESSAGE_BODY = os.getenv('MESSAGE_BODY', '')

    # Filter settings
    MIN_PRICE = float(os.getenv('MIN_PRICE', 0))
    MAX_PRICE = float(os.getenv('MAX_PRICE', 999999))
    CATEGORIES = os.getenv('CATEGORIES', '').split(',') if os.getenv('CATEGORIES') else []

    # Bot settings
    MAX_MESSAGES_PER_RUN = int(os.getenv('MAX_MESSAGES_PER_RUN', 100))
    DELAY_BETWEEN_REQUESTS = int(os.getenv('DELAY_BETWEEN_REQUESTS', 2))

    # Database
    DB_PATH = 'bot_data.db'

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []

        if not cls.SENDER_EMAIL:
            errors.append("SENDER_EMAIL is required")
        if not cls.SENDER_PASSWORD:
            errors.append("SENDER_PASSWORD is required")
        if not cls.MARKETPLACE_URL:
            errors.append("MARKETPLACE_URL is required")
        if not cls.MESSAGE_BODY:
            errors.append("MESSAGE_BODY is required")

        return errors
