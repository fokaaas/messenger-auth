# Telegram-Integrated Registration System with 2FA

Flask web application implementing secure multi-step user registration with phone verification via Telegram and TOTP-based two-factor authentication.

## Features

- Phone number verification via Telegram OTP (6-digit code, 5-minute expiry)
- Strong password enforcement (8+ chars, uppercase, lowercase, digit, special character)
- TOTP-based 2FA with QR code for authenticator apps (Google Authenticator, Authy, etc.)
- Password hashing with bcrypt
- SQLite storage

## Project Structure

```
├── app/
│   ├── __init__.py               # Flask app factory, DB init
│   ├── config.py                 # Configuration from .env
│   ├── routes/
│   │   └── registration.py       # Multi-step registration workflow
│   ├── services/
│   │   ├── database.py           # SQLite operations
│   │   ├── otp_service.py        # OTP generation and verification
│   │   └── telegram_service.py   # Telegram bot API integration
│   ├── templates/                # Jinja2 templates
│   │   ├── register.html         # Step 1: Phone + Chat ID
│   │   ├── verify.html           # Step 2: OTP verification
│   │   ├── password.html         # Step 3: Password creation
│   │   ├── setup_2fa.html        # Step 4: QR code for 2FA
│   │   └── complete.html         # Success page
│   └── utils/
│       └── validators.py         # Password validation rules
├── bot.py                        # Telegram bot (provides Chat ID)
├── run.py                        # Entry point
├── requirements.txt              # Dependencies
└── .env                          # Environment variables
```

## Requirements

- Python 3.8+
- Telegram bot token (obtain from [@BotFather](https://t.me/BotFather))

## Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
BOT_TOKEN=your_telegram_bot_token
SECRET_KEY=your_flask_secret_key
```

## Usage

1. Start the Telegram bot to allow users to obtain their Chat ID:

```bash
python bot.py
```

2. Start the Flask web application:

```bash
python run.py
```

The app runs at `http://localhost:5000`.

## Registration Flow

1. User sends `/start` to the Telegram bot to get their Chat ID
2. User opens the web app and enters phone number + Chat ID
3. A 6-digit OTP is sent to the user via Telegram
4. User verifies the OTP code
5. User creates a strong password
6. User scans a QR code with an authenticator app and confirms the TOTP code
7. Registration is complete, user data is saved to the database

## Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    totp_secret TEXT NOT NULL,
    chat_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Dependencies

- Flask
- python-telegram-bot
- requests
- bcrypt
- pyotp
- qrcode[pil]
- python-dotenv
