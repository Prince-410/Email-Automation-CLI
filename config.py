"""
config.py - SMTP Configuration Loader

Loads SMTP configuration from a .env file using python-dotenv.
Validates that all required environment variables are present.
"""

import os
from dotenv import load_dotenv


def get_smtp_config() -> dict:
    """
    Loads SMTP configuration from a .env file and validates it.

    Returns a dictionary with all configuration values, using keys
    that are consistent with the sender module expectations:
        - host, port, user, password, sender_email, sender_name

    Raises:
        ValueError: If any required environment variable is missing
                    or SMTP_PORT is not a valid integer.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Define required environment variables
    required_vars = [
        "SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME",
        "SMTP_PASSWORD", "SENDER_EMAIL", "SENDER_NAME"
    ]

    # Check for missing variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please check your .env file."
        )

    # Validate SMTP_PORT is a valid integer
    try:
        smtp_port = int(os.getenv("SMTP_PORT"))
    except (ValueError, TypeError):
        raise ValueError("SMTP_PORT must be a valid integer (e.g., 587 or 465).")

    # Return config dict with sender-module-compatible keys
    config = {
        "host": os.getenv("SMTP_HOST"),
        "port": smtp_port,
        "user": os.getenv("SMTP_USERNAME"),
        "password": os.getenv("SMTP_PASSWORD"),
        "sender_email": os.getenv("SENDER_EMAIL"),
        "sender_name": os.getenv("SENDER_NAME"),
    }

    return config
