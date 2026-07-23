# 📧 Email Automation CLI

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A powerful, command-line interface tool for automating personalized email campaigns. Send beautiful HTML emails to bulk recipients with attachments, scheduling, and templating support.

## ✨ Features

- **Personalized Templating:** Uses Jinja2 for dynamic HTML email content.
- **Bulk Sending:** Reads recipient data from CSV files.
- **Attachments:** Send files or entire directories as email attachments.
- **Scheduling:** Schedule emails to be sent at a specific date and time.
- **Dry Run Mode:** Test your campaigns without actually sending any emails.
- **Environment Variables:** Securely store your credentials using `.env`.

## 📁 Project Structure

```
Email Automation/
├── main.py               # CLI entry point
├── config.py             # SMTP configuration loader
├── sender.py             # Email sending engine
├── scheduler.py          # Email scheduling
├── template.py           # Jinja2 template handling
├── logger.py             # Logging setup
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── .env                  # SMTP credentials (edit this!)
├── templates/
│   └── email.html        # HTML email template
├── attachments/          # Place files to attach here
├── data/
│   └── recipients.csv    # Recipient list (name, email)
└── logs/                 # Delivery logs (auto-created)
```

## 🛠 Prerequisites

- Python 3.8 or higher
- An SMTP server (e.g., Gmail)

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/email-automation.git
   cd email-automation
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. Create a `.env` file in the root directory (you can copy the provided sample).
2. Configure your SMTP settings:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
SENDER_NAME=Your Name
```

### 🔐 Gmail App Password Instructions
If you are using Gmail, you cannot use your regular password if 2-Step Verification is enabled. Instead, you need to create an App Password:
1. Go to your Google Account settings.
2. Navigate to **Security**.
3. Under "Signing in to Google," select **2-Step Verification**.
4. At the bottom, click on **App passwords**.
5. Generate a password for "Mail" and use that in your `.env` file for `SMTP_PASSWORD`.

## 📖 Usage Examples

Here are some common ways to use the Email Automation CLI:

**Basic send:**
```bash
python main.py -s "Subject" -c data/recipients.csv
```

**With attachments:**
```bash
python main.py -s "Subject" -a attachments/
```

**Scheduled send:**
```bash
python main.py -s "Subject" -S "2024-12-25 09:00"
```

**Dry run (test without sending):**
```bash
python main.py -s "Subject" --dry-run
```

## 🎨 Template Customization

The project uses Jinja2 for templating. You can edit `templates/email.html` to customize the design. Use `{{name}}` to insert the recipient's name dynamically based on the CSV data.

*Note: It is recommended to use inline CSS for HTML emails to ensure maximum compatibility across different email clients.*

## 📋 CSV Format

The CSV file must contain at least two columns: `name` and `email`.

```csv
name,email
Alice Johnson,alice.johnson@example.com
Bob Smith,bob.smith@example.com
```

## ❓ Troubleshooting

- **Authentication Failed (Gmail):** Ensure you are using an App Password and not your regular account password.
- **Connection Refused/Timeout:** Check your firewall settings and ensure your network allows outgoing connections on your SMTP port (e.g., 587 or 465).
- **Missing Dependencies:** Make sure you have activated your virtual environment and run `pip install -r requirements.txt`.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
