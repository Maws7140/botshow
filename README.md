# Automated Messaging Bot

An intelligent bot that automatically scans marketplace product pages, extracts contact information, and sends targeted messages to contacts with Chinese phone numbers (+86).

## Features

✅ **Automated Product Scanning** - Continuously browse marketplace product pages
✅ **Smart Contact Extraction** - Extract name, email, phone, and business info
✅ **Intelligent Filtering** - Filter by phone prefix (+86), price range, and categories
✅ **Duplicate Prevention** - Track contacted vendors to avoid duplicate messages
✅ **Customizable Messages** - User-defined message templates with personalization
✅ **Filter Options** - Price ranges, category inclusion/exclusion
✅ **Automatic Retry** - Handle phone number changes and recheck eligibility
✅ **Statistics Tracking** - Comprehensive analytics and reporting
✅ **Safe & Controlled** - Start/stop controls, rate limiting, and error handling

## Requirements

- Python 3.8 or higher
- Chrome or Chromium browser (for web scraping)
- Email account with SMTP access (Gmail recommended)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd botshow
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Bot

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and configure your settings:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Marketplace Configuration
MARKETPLACE_URL=https://example-marketplace.com/products

# Message Template
MESSAGE_SUBJECT=Business Opportunity
MESSAGE_BODY=Hello, we would like to discuss a business opportunity with you.

# Filters
MIN_PRICE=10
MAX_PRICE=1000
CATEGORIES=electronics,clothing,accessories

# Bot Settings
MAX_MESSAGES_PER_RUN=100
DELAY_BETWEEN_REQUESTS=2
```

### 4. Gmail Setup (if using Gmail)

For Gmail, you need to create an **App Password**:

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → App Passwords
4. Generate a new app password for "Mail"
5. Use this password in the `SENDER_PASSWORD` field

## Usage

### Interactive Mode (Recommended)

Run the bot in interactive mode with a menu:

```bash
python main.py --interactive
```

Or simply:

```bash
python main.py
```

The interactive menu allows you to:
- Start/stop the bot
- View statistics
- Configure filters
- Update message templates
- Test email connection

### Direct Mode

Start the bot directly:

```bash
python main.py
```

Stop the bot anytime by pressing `Ctrl+C`.

### Command Line Options

```bash
# Show statistics
python main.py --stats

# Test email connection
python main.py --test-email

# Run in non-headless mode (show browser)
python main.py --headless=False
```

## How It Works

### Main Workflow

1. **Scan Products** - Bot browses marketplace product pages automatically
2. **Extract Contacts** - For each product, opens contact details section
3. **Apply Filters** - Checks if product matches price/category filters
4. **Validate Phone** - Checks if phone number starts with +86 (China)
5. **Check Database** - Verifies contact hasn't been messaged before
6. **Send Message** - Sends email to qualifying contacts
7. **Track Contact** - Marks contact as messaged in database
8. **Continue** - Repeats until stopped or limit reached

### Message Rules

✅ **Message Sent When:**
- Phone number starts with +86
- Email address is present
- Contact hasn't been messaged before
- Product matches filters (price, category)

❌ **Message NOT Sent When:**
- Phone number doesn't start with +86
- No email address found
- Contact already messaged
- Product doesn't match filters

### Revisit Logic

- Once a contact is messaged, they are marked as "contacted"
- Bot skips already-contacted vendors to save time
- If a contact later changes their phone TO +86, bot will detect and message them
- Database tracks all contacts for reference

## Configuration

### Price Filters

Set minimum and maximum price ranges:

```env
MIN_PRICE=10
MAX_PRICE=1000
```

### Category Filters

Include specific categories (comma-separated):

```env
CATEGORIES=electronics,clothing,accessories
```

Leave empty to include all categories:

```env
CATEGORIES=
```

### Message Template

Customize your message:

```env
MESSAGE_SUBJECT=Business Opportunity
MESSAGE_BODY=Hello,

We are interested in your products and would like to discuss a potential business partnership.

Best regards,
Your Company Name
```

The bot automatically personalizes messages by adding the contact's name if available.

### Rate Limiting

Control request speed to avoid being blocked:

```env
DELAY_BETWEEN_REQUESTS=2  # seconds between requests
MAX_MESSAGES_PER_RUN=100  # maximum messages per session
```

## Database

The bot uses SQLite to track contacts:

- **File**: `bot_data.db`
- **Location**: Project root directory

### Database Schema

```sql
contacts (
    email TEXT UNIQUE,
    phone TEXT,
    name TEXT,
    business_info TEXT,
    product_url TEXT,
    contacted_at TIMESTAMP,
    message_sent BOOLEAN,
    created_at TIMESTAMP
)
```

### View Database Stats

```bash
python main.py --stats
```

## Logs

All bot activity is logged to:

- **Console**: Colored output with icons
- **File**: `logs/bot.log`

Log levels:
- ℹ Info (cyan)
- ✓ Success (green)
- ⚠ Warning (yellow)
- ✗ Error (red)

## Customization

### Custom Marketplace

To use with a different marketplace, you may need to customize:

1. **Contact Selectors** - Edit `web_scraper.py` to match your marketplace's HTML structure
2. **Price Extraction** - Adjust price selectors in `extract_price()` method
3. **Category Extraction** - Adjust category selectors in `extract_category()` method

Example:

```python
# In web_scraper.py
contact_selectors = [
    "//button[contains(text(), 'Contact Seller')]",  # Your marketplace's contact button
    ".contact-info-section",  # Your marketplace's contact section
]
```

### Custom Message Logic

Edit `contact_extractor.py` to change the phone validation logic:

```python
@staticmethod
def is_valid_china_number(phone: str) -> bool:
    """Customize phone validation logic here"""
    return phone.startswith('+86')
```

## Safety & Best Practices

⚠️ **Important Considerations:**

1. **Rate Limiting** - Always use appropriate delays to avoid being blocked
2. **Terms of Service** - Ensure your usage complies with marketplace ToS
3. **Email Limits** - Respect email provider sending limits (Gmail: ~500/day)
4. **Testing** - Test thoroughly with a small dataset first
5. **Monitoring** - Regularly check logs for errors
6. **Backups** - Backup `bot_data.db` regularly

## Troubleshooting

### Bot Can't Find Products

- Check if `MARKETPLACE_URL` is correct
- Verify marketplace structure hasn't changed
- Try running in non-headless mode to see what's happening
- Check `logs/bot.log` for details

### Email Sending Fails

- Verify email credentials in `.env`
- For Gmail, ensure you're using an App Password
- Check SMTP server and port settings
- Test connection: `python main.py --test-email`

### Browser/WebDriver Issues

```bash
# Update Chrome driver
pip install --upgrade webdriver-manager

# Or manually download ChromeDriver matching your Chrome version
```

### Database Locked

If you get "database is locked" errors:
- Ensure only one bot instance is running
- Check if any other process is accessing `bot_data.db`

## Architecture

```
┌─────────────────┐
│   main.py       │  CLI & Menu Interface
└────────┬────────┘
         │
┌────────▼────────┐
│ bot_controller  │  Main Orchestration
└────────┬────────┘
         │
    ┌────┴────┬────────┬──────────┬──────────┐
    │         │        │          │          │
┌───▼──┐  ┌──▼───┐ ┌──▼────┐  ┌──▼────┐  ┌─▼─────┐
│ web_ │  │email_│ │contact│  │filter │  │data   │
│scraper  sender│ │extract│  │       │  │base   │
└──────┘  └──────┘ └───────┘  └───────┘  └───────┘
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational and legitimate business purposes.

## Support

For issues, questions, or feature requests, please create an issue in the repository.

## Disclaimer

This bot is designed for legitimate business outreach. Users are responsible for:
- Complying with all applicable laws and regulations
- Respecting marketplace terms of service
- Following email marketing best practices
- Obtaining necessary permissions for automated scraping
- Respecting privacy and anti-spam regulations (GDPR, CAN-SPAM, etc.)

Use responsibly and ethically.
