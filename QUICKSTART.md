# Quick Start Guide

Get your automated messaging bot running in 5 minutes!

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Your Settings

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your details:

```env
# Required: Your email credentials
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password

# Required: Target marketplace URL
MARKETPLACE_URL=https://example-marketplace.com/products

# Required: Your message
MESSAGE_SUBJECT=Business Inquiry
MESSAGE_BODY=Hello, I am interested in your products...

# Optional: Filters
MIN_PRICE=10
MAX_PRICE=1000
CATEGORIES=electronics,accessories
```

### Gmail App Password Setup (2 minutes)

1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"
3. Go to https://myaccount.google.com/apppasswords
4. Create password for "Mail"
5. Copy the 16-character password to `SENDER_PASSWORD`

## Step 3: Test Your Configuration

```bash
# Test email connection
python main.py --test-email
```

You should see: `✓ Email connection test successful`

## Step 4: Run the Bot!

### Option A: Interactive Mode (Recommended for First Time)

```bash
python main.py --interactive
```

Then select option 1 to start the bot.

### Option B: Direct Mode

```bash
python main.py
```

Press `Ctrl+C` to stop anytime.

## Step 5: Monitor Progress

Watch the console for real-time updates:

```
[1/50] Processing: https://example.com/product/123
  Contact: John Doe
  Email: john@example.com
  Phone: +8613812345678
  ✓ Phone starts with +86 - sending message
  ✓ Email sent successfully to john@example.com
```

## Next Steps

### View Statistics

```bash
python main.py --stats
```

### Customize Filters

Edit `.env` or use interactive mode (option 3) to:
- Set price ranges (MIN_PRICE, MAX_PRICE)
- Filter categories (CATEGORIES)
- Adjust rate limits (DELAY_BETWEEN_REQUESTS)

### Check Logs

All activity is logged to `logs/bot.log`

## Common Issues

### ❌ "Email connection failed"
- Check your Gmail app password (not regular password!)
- Verify 2FA is enabled on your Google account
- Make sure SMTP settings are correct

### ❌ "No products found"
- Verify MARKETPLACE_URL is correct
- Marketplace structure may need customization (see README)

### ❌ "WebDriver error"
- Chrome must be installed
- Run: `pip install --upgrade webdriver-manager`

## Tips

1. **Start Small** - Test with `MAX_MESSAGES_PER_RUN=10` first
2. **Use Delays** - Set `DELAY_BETWEEN_REQUESTS=3` to avoid blocks
3. **Monitor Logs** - Check `logs/bot.log` regularly
4. **Backup Database** - Copy `bot_data.db` periodically

## Need Help?

- Read the full [README.md](README.md) for detailed documentation
- Check `logs/bot.log` for error details
- Create an issue in the repository

---

**You're all set! 🚀**

The bot will now automatically:
- Scan marketplace products
- Extract contact information
- Send messages to +86 phone contacts
- Track everything in the database
- Skip duplicates automatically
