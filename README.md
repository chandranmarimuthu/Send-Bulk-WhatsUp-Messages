# 💬 WhatsApp Bulk Message Sender

Automated tool to send WhatsApp messages to multiple contacts from a CSV file. Uses Selenium to open WhatsApp Web once and send messages one-by-one, avoiding WhatsApp's rate limiting policies.

## ✨ Features

- ✅ **Single Browser Session** - Opens WhatsApp Web once, sends all messages from same session
- ✅ **Bulk Send** - Send messages to hundreds of contacts automatically
- ✅ **CSV Support** - Load contacts from CSV with custom columns
- ✅ **Personalization** - Use contact names and custom fields in messages
- ✅ **Rate Limiting** - Configurable delays between messages to avoid bans
- ✅ **Error Handling** - Track failed messages with detailed logs
- ✅ **Web UI** - Streamlit interface for easy management
- ✅ **Progress Tracking** - Real-time status updates
- ✅ **Tamil Support** - Full UTF-8 encoding support for Tamil names

## 📋 Requirements

- **Python 3.8+**
- **Google Chrome** or **Brave Browser** (for WhatsApp Web automation)
- **WhatsApp Account** with Web access enabled
- **Internet Connection**

## 🚀 Installation

### 1. Create Virtual Environment
```bash
cd WhatsupBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key packages:**
- `selenium>=4.0.0` - Browser automation
- `webdriver-manager>=3.8.0` - Automatic Chrome driver management
- `streamlit>=1.28.0` - Web UI
- `pandas>=2.0.0` - CSV handling

## 📖 How to Use

### Step 1: Prepare CSV File

Create a CSV with at least these columns:
- `phone_number` - Phone number (e.g., 90000002212 or +9190000002212)
- `name` - Contact name for personalization

Optional columns can be added and used in message template.

**Example:**
```csv
phone_number,name
90000002212,Chandran Marimuthu
```

### Step 2: Run Streamlit App
```bash
python -m streamlit run app.py
```

Browser opens at `http://localhost:8502` (or next available port)

### Step 3: Upload CSV and Compose Message

1. Upload your CSV file
2. Preview contacts to verify data is correct
3. Write message with `{name}` placeholder for personalization
4. Set delay between messages (5-10 seconds recommended)
5. Click "🚀 Start Sending Messages"

### Step 4: Scan QR Code

- WhatsApp Web opens in new Chrome window
- Scan QR code with your phone **if needed** (will prompt if not logged in)
- Messages start sending automatically one by one
- **Keep browser window open** until all messages send
- Browser closes automatically when done

## 📝 Message Template Guide

Use curly braces `{}` to insert contact fields:

```
Hi {name}! 👋

I'm from {company} and we have a special {offer} offer for you.

Would you like to know more?

Best regards
```

The app will personalize with values from your CSV columns for each contact.

## ⚙️ Settings

- **Delay between messages**: Seconds to wait between each message (default: 5)
  - Higher = safer, lower risk of rate limiting
  - Minimum: 2 seconds
  - Recommended: 5-10 seconds for safety
  - Use 15-30 seconds if account is new

## 🎯 How It Works

1. **Single Session** - Opens WhatsApp Web once (not multiple times)
2. **URL Injection** - Sends message content via WhatsApp's Web URL parameter
3. **One-by-one** - Waits between each contact to avoid rate limiting
4. **Auto-send** - Uses Selenium to click Send button automatically

**Why this approach?**
- ✅ Avoids "too many requests" errors
- ✅ Reduces account flagging risk
- ✅ Better WhatsApp compliance
- ✅ More reliable than pywhatkit



## ⚠️ Important Notes

### WhatsApp Limits
- Don't send too many messages too quickly
- WhatsApp may flag/ban accounts sending bulk messages
- Use delays: 5-10 seconds **minimum** between messages
- Test with small groups first (5-10 messages)
- Avoid sending at odd hours (WhatsApp detects bot patterns)

### Best Practices
1. **Small batches** - Start with 5-10 messages and monitor
2. **Proper delays** - Use 5-10 second minimum delays
3. **Personalize** - Always use contact names in messages (looks more human)
4. **Authentic content** - Messages should provide real value
5. **Respect opt-in** - Only message people who want to receive messages
6. **Monitor first batch** - Check if messages deliver before sending more
7. **Varied timing** - Don't send all messages at same time of day

### Technical Notes
- **Phone number format** - App accepts both `90000002212` and `+9190000002212`
- **Browser must stay open** - Keep Chrome/Brave window open during sending
- **QR code** - Only needed if WhatsApp Web session expired
- **UTF-8 encoding** - Full support for Tamil, Hindi, and other languages
- **Selenium automation** - Uses official WhatsApp Web, no third-party API

## 🔧 Command Line Usage

You can also use the sender programmatically:

```python
from whatsapp_sender import WhatsAppBulkSender

# Initialize
sender = WhatsAppBulkSender("contacts.csv", wait_time=5)

# Load contacts
if sender.load_contacts():
    # Send messages (opens browser once)
    message = "Hi {name}! This is a test message."
    result = sender.send_bulk_messages(message, delay_seconds=5)
    
    # Get report
    report = sender.get_report()
    print(f"✅ Sent: {report['summary']['total_sent']}")
    print(f"❌ Failed: {report['summary']['total_failed']}")
    print(f"📊 Success Rate: {report['summary']['success_rate']:.1f}%")
```

## 📊 Reports

After sending, view:
- ✅ Count of successfully sent messages
- ❌ Failed messages with error details
- ⏱️ Timestamp of each message attempt
- 📈 Success rate percentage

## 🐛 Troubleshooting

### "Browser not opening"
- Ensure Chrome or Brave is installed
- Try with Brave instead of Chrome
- Check if another app is blocking port 9515 (Selenium ChromeDriver port)
- Run: `Get-Process -Name "chromedriver" | Stop-Process -Force` to kill stuck drivers

### "WhatsApp Web not loading"
- Check internet connection
- Try in Incognito/Private mode first
- Clear Chrome cache: `chrome://settings/clearBrowserData`
- Make sure WhatsApp is accessible in your region

### "Rate limited / Account flagged"
- Stop sending immediately
- Wait 24-48 hours before sending again
- Increase delays to 10-15 seconds for next batch
- Use smaller batches (5-10 messages)
- Consider WhatsApp Business API for commercial use

### "Phone number not recognized"
- Remove spaces, hyphens, parentheses
- Format: `90000002212` or `+9190000002212`
- Example for UK: `+442071234567`
- Example for USA: `+12025551234`
- Verify number is correct (has country code)

### "Phone number is integer"
- CSV might be storing numbers as integers
- Fix: Add a leading `'` in CSV or format in Excel as Text
- The app auto-converts now, but Excel can lose leading zeros

## 📝 CSV Format Examples

### Minimal (Required)
```csv
phone_number,name
90000002212,Chandran Marimuthu
```

### With Custom Fields
```csv
phone_number,name
90000002212,Chandran Marimuthu
```

### With International Numbers
```csv
phone_number,name
90000002212,Chandran Marimuthu
```

### Use in Message Template
```
Hi {name}!

We at {company} are offering {discount} off on our {product}.

This offer is valid for {country} region only.

Interested? Reply ASAP!
```

## 🔐 Privacy & Legal

- ⚠️ **Only send messages to contacts who gave consent**
- ⚠️ **Don't spam** - Unsolicited messages violate WhatsApp ToS
- ⚠️ **Check local laws** - Bulk messaging regulations vary by country
- ⚠️ **Include opt-out** - Messages should allow recipients to unsubscribe
- ⚠️ **Account risk** - WhatsApp may temporarily/permanently ban accounts doing bulk messaging
- ℹ️ **Business API** - For commercial use, WhatsApp Business API is recommended

## 📱 WhatsApp Business API (Recommended for Production)

For commercial bulk messaging, use **WhatsApp Business API** instead of this tool:
- ✅ Official WhatsApp channel
- ✅ Higher rate limits (100,000+ messages/day)
- ✅ Better compliance
- ✅ Professional support
- ✅ Templates and approved messages
- ✅ No account ban risk

This tool is for **personal use** or **small batches**. For business, use official API.

## 🎯 Next Steps

1. **Prepare CSV** - Create your contacts list
2. **Test locally** - Run `python -m streamlit run app.py`
3. **Send test batch** - Upload CSV and send to 5-10 contacts
4. **Monitor results** - Check if messages deliver successfully
5. **Gradually increase** - Increase batch size if no issues
6. **Adjust delays** - Set appropriate delays based on account age

## ❓ FAQ

**Q: Can I send to international numbers?**
A: Yes! Use format: `+{country_code}{number}` (e.g., `+442071234567` for UK, `+12025551234` for USA)

**Q: How many messages can I send per day?**
A: Depends on account age and WhatsApp's algorithms. Start with 20-50/day. Increase gradually if no issues.

**Q: Will my account get banned?**
A: Risk of temporary or permanent ban if sending spam/unsolicited messages. Always personalize, use delays, and get consent.

**Q: Can I schedule messages for later?**
A: Not in this version. You can schedule the Python script using Windows Task Scheduler or cron (Mac/Linux).

**Q: Does it work on Mac/Linux?**
A: Yes! Install Chrome or Brave and follow the same steps. Works on Windows, Mac, and Linux.

**Q: What if browser closes during sending?**
A: Messages in progress will fail. Keep browser window open until "Completed" message appears.

**Q: Can I resume interrupted sends?**
A: Not automatically, but the app shows which messages failed. Resend only to failed contacts.

## 💡 Support

For issues:
1. **Check troubleshooting** section above
2. **Verify CSV format** - Use provided template
3. **Test with 1-2 messages** - Before large batch
4. **Check browser console** - Right-click → Inspect → Console tab
5. **Try different browser** - Chrome vs Brave
6. **Check logs** - Look at terminal output for error details

---

**Disclaimer:** This tool is for personal use only. Users are responsible for complying with WhatsApp's Terms of Service and local laws. The authors are not responsible for account bans or other consequences.

**Happy messaging! 💬✨**
