#!/usr/bin/env python3
"""
Automated Messaging Bot - Main Entry Point

This bot automatically scans marketplace product pages, extracts contact information,
and sends messages to contacts with phone numbers starting with +86.
"""
import argparse
import sys
from config import Config
from bot_controller import MessagingBot
from database import ContactDatabase


def print_banner():
    """Print application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         AUTOMATED MESSAGING BOT                           ║
║         Version 1.0.0                                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_config_errors(errors):
    """Print configuration validation errors."""
    print("\n❌ Configuration Errors:")
    for error in errors:
        print(f"   • {error}")
    print("\nPlease create a .env file with the required settings.")
    print("See .env.example for reference.\n")


def show_stats(db_path: str):
    """Show database statistics."""
    db = ContactDatabase(db_path)
    stats = db.get_stats()

    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    print(f"Total contacts:       {stats['total_contacts']}")
    print(f"Contacted:            {stats['contacted']}")
    print(f"Pending:              {stats['pending']}")
    print(f"China contacts (+86): {stats['china_contacts']}")
    print("="*60 + "\n")


def interactive_mode():
    """Run bot in interactive mode with menu."""
    print_banner()

    # Validate configuration
    errors = Config.validate()
    if errors:
        print_config_errors(errors)
        return

    bot = None

    while True:
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Start Bot")
        print("2. View Statistics")
        print("3. Configure Filters")
        print("4. Update Message Template")
        print("5. Test Email Connection")
        print("6. Exit")
        print("="*60)

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == '1':
            # Start bot
            print("\n🚀 Starting bot...")
            print("Press Ctrl+C to stop the bot at any time.\n")

            headless = input("Run browser in headless mode? (y/n) [y]: ").strip().lower()
            headless = headless != 'n'

            try:
                bot = MessagingBot(Config)
                bot.start(headless=headless)
            except KeyboardInterrupt:
                print("\n\n⚠ Bot stopped by user")
            except Exception as e:
                print(f"\n❌ Error: {e}")
            finally:
                if bot:
                    bot.stop()

        elif choice == '2':
            # View statistics
            show_stats(Config.DB_PATH)

        elif choice == '3':
            # Configure filters
            print("\n" + "="*60)
            print("CONFIGURE FILTERS")
            print("="*60)
            print(f"Current min price: €{Config.MIN_PRICE}")
            print(f"Current max price: €{Config.MAX_PRICE}")
            print(f"Current categories: {', '.join(Config.CATEGORIES) if Config.CATEGORIES else 'All'}")

            try:
                min_price = input(f"\nEnter minimum price [{Config.MIN_PRICE}]: ").strip()
                if min_price:
                    Config.MIN_PRICE = float(min_price)

                max_price = input(f"Enter maximum price [{Config.MAX_PRICE}]: ").strip()
                if max_price:
                    Config.MAX_PRICE = float(max_price)

                categories = input("Enter categories (comma-separated) or press Enter for all: ").strip()
                if categories:
                    Config.CATEGORIES = [c.strip() for c in categories.split(',')]

                print("\n✓ Filters updated successfully")
            except ValueError:
                print("\n❌ Invalid input. Filters not updated.")

        elif choice == '4':
            # Update message template
            print("\n" + "="*60)
            print("UPDATE MESSAGE TEMPLATE")
            print("="*60)
            print(f"Current subject: {Config.MESSAGE_SUBJECT}")
            print(f"Current body:\n{Config.MESSAGE_BODY}")

            subject = input(f"\nEnter new subject [{Config.MESSAGE_SUBJECT}]: ").strip()
            if subject:
                Config.MESSAGE_SUBJECT = subject

            print("Enter new message body (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == '' and (not lines or lines[-1] == ''):
                    break
                lines.append(line)

            if lines:
                Config.MESSAGE_BODY = '\n'.join(lines[:-1])  # Remove last empty line

            print("\n✓ Message template updated successfully")

        elif choice == '5':
            # Test email connection
            from email_sender import EmailSender
            print("\n🔍 Testing email connection...")

            sender = EmailSender(
                Config.SMTP_SERVER,
                Config.SMTP_PORT,
                Config.SENDER_EMAIL,
                Config.SENDER_PASSWORD
            )

            if sender.test_connection():
                print("✓ Email connection successful!")
            else:
                print("✗ Email connection failed. Check your credentials.")

        elif choice == '6':
            # Exit
            print("\n👋 Goodbye!\n")
            break

        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 6.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Automated Messaging Bot - Send messages to marketplace contacts'
    )

    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode with menu'
    )

    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics and exit'
    )

    parser.add_argument(
        '--test-email',
        action='store_true',
        help='Test email connection and exit'
    )

    args = parser.parse_args()

    # Show statistics
    if args.stats:
        show_stats(Config.DB_PATH)
        return

    # Test email
    if args.test_email:
        from email_sender import EmailSender
        print("Testing email connection...")
        sender = EmailSender(
            Config.SMTP_SERVER,
            Config.SMTP_PORT,
            Config.SENDER_EMAIL,
            Config.SENDER_PASSWORD
        )
        sender.test_connection()
        return

    # Interactive mode
    if args.interactive or len(sys.argv) == 1:
        interactive_mode()
        return

    # Direct mode - just start the bot
    print_banner()

    # Validate configuration
    errors = Config.validate()
    if errors:
        print_config_errors(errors)
        return

    try:
        bot = MessagingBot(Config)
        bot.start(headless=args.headless)
    except KeyboardInterrupt:
        print("\n\n⚠ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
