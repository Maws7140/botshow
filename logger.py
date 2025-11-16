"""
Logging module for the bot.
"""
import logging
from datetime import datetime
import os


class BotLogger:
    """Custom logger for the messaging bot."""

    # ANSI color codes
    COLORS = {
        'RESET': '\033[0m',
        'RED': '\033[91m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'BLUE': '\033[94m',
        'MAGENTA': '\033[95m',
        'CYAN': '\033[96m',
        'WHITE': '\033[97m',
    }

    def __init__(self, log_file: str = 'bot.log', console_output: bool = True):
        """
        Initialize logger.

        Args:
            log_file: Path to log file
            console_output: Whether to output to console
        """
        self.log_file = log_file
        self.console_output = console_output

        # Setup file logger
        self.logger = logging.getLogger('MessagingBot')
        self.logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)

        # File handler
        fh = logging.FileHandler(f'logs/{log_file}')
        fh.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)

        self.logger.addHandler(fh)

    def _colorize(self, message: str, color: str) -> str:
        """Add color to message."""
        return f"{self.COLORS.get(color, '')}{message}{self.COLORS['RESET']}"

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
        if self.console_output:
            print(self._colorize(f"ℹ {message}", 'CYAN'))

    def success(self, message: str):
        """Log success message."""
        self.logger.info(message)
        if self.console_output:
            print(self._colorize(f"✓ {message}", 'GREEN'))

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
        if self.console_output:
            print(self._colorize(f"⚠ {message}", 'YELLOW'))

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
        if self.console_output:
            print(self._colorize(f"✗ {message}", 'RED'))

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
        if self.console_output:
            print(self._colorize(f"🔍 {message}", 'MAGENTA'))
