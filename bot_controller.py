"""
Main bot controller that orchestrates the automated messaging system.
"""
import time
import signal
import sys
from typing import Optional
from config import Config
from database import ContactDatabase
from contact_extractor import ContactExtractor
from email_sender import EmailSender
from web_scraper import MarketplaceScraper
from filters import ProductFilter
from logger import BotLogger


class MessagingBot:
    """Main bot controller for automated messaging."""

    def __init__(self, config: Config):
        """
        Initialize the messaging bot.

        Args:
            config: Configuration object
        """
        self.config = config
        self.running = False
        self.paused = False

        # Initialize components
        self.db = ContactDatabase(config.DB_PATH)
        self.email_sender = EmailSender(
            config.SMTP_SERVER,
            config.SMTP_PORT,
            config.SENDER_EMAIL,
            config.SENDER_PASSWORD
        )
        self.scraper: Optional[MarketplaceScraper] = None
        self.filter = ProductFilter(
            min_price=config.MIN_PRICE,
            max_price=config.MAX_PRICE,
            categories=config.CATEGORIES
        )
        self.contact_extractor = ContactExtractor()
        self.logger = BotLogger()

        # Statistics
        self.stats = {
            'products_scanned': 0,
            'contacts_found': 0,
            'messages_sent': 0,
            'messages_failed': 0,
            'contacts_skipped': 0
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\n\n🛑 Received stop signal. Shutting down gracefully...")
        self.stop()

    def start(self, headless: bool = True):
        """
        Start the bot.

        Args:
            headless: Run browser in headless mode
        """
        self.logger.info("Starting Automated Messaging Bot")
        self.logger.info(f"Configuration: {self.filter.get_filter_summary()}")

        # Test email connection
        self.logger.info("Testing email connection...")
        if not self.email_sender.test_connection():
            self.logger.error("Email connection failed. Please check your credentials.")
            return

        # Initialize scraper
        try:
            self.scraper = MarketplaceScraper(headless=headless)
        except Exception as e:
            self.logger.error(f"Failed to initialize web scraper: {e}")
            return

        self.running = True
        self.logger.info("Bot started successfully. Press Ctrl+C to stop.\n")

        try:
            self._run_bot_loop()
        except Exception as e:
            self.logger.error(f"Bot encountered an error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the bot and cleanup resources."""
        if not self.running:
            return

        self.running = False
        self.logger.info("\nStopping bot...")

        if self.scraper:
            self.scraper.close()

        # Print final statistics
        self._print_statistics()
        self.logger.info("Bot stopped successfully.")

    def pause(self):
        """Pause the bot."""
        self.paused = True
        self.logger.info("Bot paused.")

    def resume(self):
        """Resume the bot."""
        self.paused = False
        self.logger.info("Bot resumed.")

    def _run_bot_loop(self):
        """Main bot execution loop."""
        # Get product links
        self.logger.info(f"Scanning marketplace: {self.config.MARKETPLACE_URL}")
        product_links = self.scraper.get_product_links(
            self.config.MARKETPLACE_URL,
            max_pages=50
        )

        if not product_links:
            self.logger.warning("No product links found. Please check the marketplace URL.")
            return

        self.logger.info(f"Found {len(product_links)} products to process\n")

        # Process each product
        messages_sent_this_run = 0

        for idx, product_url in enumerate(product_links, 1):
            if not self.running:
                break

            # Check pause state
            while self.paused and self.running:
                time.sleep(1)

            if not self.running:
                break

            # Check message limit
            if messages_sent_this_run >= self.config.MAX_MESSAGES_PER_RUN:
                self.logger.info(f"\nReached message limit ({self.config.MAX_MESSAGES_PER_RUN}). Stopping.")
                break

            self.logger.info(f"[{idx}/{len(product_links)}] Processing: {product_url}")

            try:
                # Get contact page HTML
                contact_html = self.scraper.get_contact_page_html(product_url)
                if not contact_html:
                    self.logger.warning("Could not retrieve contact information")
                    continue

                self.stats['products_scanned'] += 1

                # Extract price and category for filtering
                price = self.scraper.extract_price(contact_html)
                category = self.scraper.extract_category(contact_html)

                # Apply filters
                if not self.filter.should_process_product(price, category):
                    self.logger.info(f"Skipped - doesn't match filters (Price: {price}, Category: {category})")
                    continue

                # Extract contact information
                contact_info = self.contact_extractor.extract_contact_info(contact_html)

                if not contact_info.get('email'):
                    self.logger.warning("No email found")
                    continue

                self.stats['contacts_found'] += 1
                email = contact_info['email']
                phone = contact_info.get('phone', '')
                name = contact_info.get('name', '')

                self.logger.info(f"  Contact: {name if name else 'N/A'}")
                self.logger.info(f"  Email: {email}")
                self.logger.info(f"  Phone: {phone}")

                # Check if already contacted
                if self.db.is_contacted(email):
                    self.logger.info("  ⏭  Already contacted - skipping")
                    self.stats['contacts_skipped'] += 1
                    continue

                # Add/update contact in database
                existing_contact = self.db.get_contact_by_email(email)
                if existing_contact:
                    # Update phone if changed
                    if existing_contact['phone'] != phone:
                        self.db.update_contact_phone(email, phone)
                else:
                    # Add new contact
                    self.db.add_contact(
                        email=email,
                        phone=phone,
                        name=name,
                        business_info=contact_info.get('business_info', ''),
                        product_url=product_url
                    )

                # Check if should send message (phone starts with +86)
                if self.contact_extractor.should_send_message(contact_info):
                    self.logger.info("  ✓ Phone starts with +86 - sending message")

                    # Send email
                    success = self.email_sender.send_email(
                        recipient_email=email,
                        subject=self.config.MESSAGE_SUBJECT,
                        body=self.config.MESSAGE_BODY,
                        contact_name=name
                    )

                    if success:
                        self.db.mark_as_contacted(email)
                        self.stats['messages_sent'] += 1
                        messages_sent_this_run += 1
                        self.logger.success(f"  ✓ Message sent successfully ({messages_sent_this_run}/{self.config.MAX_MESSAGES_PER_RUN})")
                    else:
                        self.stats['messages_failed'] += 1
                        self.logger.error("  ✗ Failed to send message")
                else:
                    self.logger.info(f"  ⏭  Phone does not start with +86 - skipping message")
                    self.stats['contacts_skipped'] += 1

            except Exception as e:
                self.logger.error(f"Error processing product: {e}")

            # Delay between requests
            if self.running:
                time.sleep(self.config.DELAY_BETWEEN_REQUESTS)

        self.logger.info("\n✓ Completed processing all products")

    def _print_statistics(self):
        """Print bot statistics."""
        self.logger.info("\n" + "="*50)
        self.logger.info("FINAL STATISTICS")
        self.logger.info("="*50)
        self.logger.info(f"Products scanned:     {self.stats['products_scanned']}")
        self.logger.info(f"Contacts found:       {self.stats['contacts_found']}")
        self.logger.info(f"Messages sent:        {self.stats['messages_sent']}")
        self.logger.info(f"Messages failed:      {self.stats['messages_failed']}")
        self.logger.info(f"Contacts skipped:     {self.stats['contacts_skipped']}")

        # Database stats
        db_stats = self.db.get_stats()
        self.logger.info(f"\nDatabase Statistics:")
        self.logger.info(f"Total contacts:       {db_stats['total_contacts']}")
        self.logger.info(f"Contacted:            {db_stats['contacted']}")
        self.logger.info(f"Pending:              {db_stats['pending']}")
        self.logger.info(f"China contacts (+86): {db_stats['china_contacts']}")
        self.logger.info("="*50 + "\n")

    def get_statistics(self):
        """Get current bot statistics."""
        return {
            **self.stats,
            'database': self.db.get_stats()
        }

    def update_message(self, subject: str, body: str):
        """Update the message template."""
        self.config.MESSAGE_SUBJECT = subject
        self.config.MESSAGE_BODY = body
        self.logger.info("Message template updated")

    def update_filters(self, min_price: float = None, max_price: float = None,
                      categories: list = None):
        """Update product filters."""
        if min_price is not None:
            self.filter.min_price = min_price
        if max_price is not None:
            self.filter.max_price = max_price
        if categories is not None:
            self.filter.update_categories(categories)

        self.logger.info("Filters updated")
        self.logger.info(self.filter.get_filter_summary())
