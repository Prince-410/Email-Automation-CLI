import os
import re
import pandas as pd
import logging

logger = logging.getLogger('email_automation.utils')

def validate_email(email: str) -> bool:
    """
    Validates email format using regex.
    """
    if not isinstance(email, str):
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def load_recipients(csv_path: str) -> pd.DataFrame:
    """
    Loads CSV with columns 'name' and 'email', validates each email, 
    logs warnings for invalid ones, returns only valid rows.
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        logger.error(f"Failed to read CSV file {csv_path}: {e}")
        return pd.DataFrame()
        
    if 'name' not in df.columns or 'email' not in df.columns:
        logger.error("CSV must contain 'name' and 'email' columns.")
        return pd.DataFrame()
        
    valid_mask = df['email'].apply(validate_email)
    
    invalid_emails = df[~valid_mask]['email']
    for invalid in invalid_emails:
        logger.warning(f"Invalid email found and skipped: {invalid}")
        
    return df[valid_mask]

def get_attachments(attachment_dir: str) -> list[str]:
    """
    Returns list of file paths from a directory.
    """
    if not os.path.isdir(attachment_dir):
        logger.error(f"Attachment directory not found: {attachment_dir}")
        return []
    
    attachments = []
    for filename in os.listdir(attachment_dir):
        filepath = os.path.join(attachment_dir, filename)
        if os.path.isfile(filepath):
            attachments.append(filepath)
    return attachments

def format_file_size(size_bytes: int) -> str:
    """
    Returns human-readable file size.
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"
