import os
import smtplib
import socket
import mimetypes
import time
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Any
import pandas as pd
import jinja2

# Import logger function
from logger import log_delivery

def create_message(sender_email: str, sender_name: str, recipient_email: str, subject: str, html_body: str, attachments: Optional[List[str]] = None) -> MIMEMultipart:
    """
    Builds a MIME email message with HTML body and optional file attachments.
    
    Args:
        sender_email (str): The sender's email address.
        sender_name (str): The sender's name.
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        html_body (str): The HTML body of the email.
        attachments (list[str], optional): List of file paths to attach. Defaults to None.
        
    Returns:
        MIMEMultipart: The constructed MIME email message.
    """
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = f"{sender_name} <{sender_email}>"
    msg['To'] = recipient_email
    
    # Attach HTML body
    msg.attach(MIMEText(html_body, 'html'))
    
    # Process attachments
    if attachments:
        for filepath in attachments:
            if not os.path.isfile(filepath):
                print(f"Warning: Attachment file not found: {filepath}")
                continue
                
            filename = os.path.basename(filepath)
            ctype, encoding = mimetypes.guess_type(filepath)
            
            if ctype is None or encoding is not None:
                # Use a generic type if one cannot be guessed or file is compressed
                ctype = 'application/octet-stream'
                
            maintype, subtype = ctype.split('/', 1)
            
            with open(filepath, 'rb') as f:
                part = MIMEBase(maintype, subtype)
                part.set_payload(f.read())
                
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            msg.attach(part)
            
    return msg

def send_email(smtp_config: Dict[str, Any], message: MIMEMultipart) -> bool:
    """
    Connects to SMTP server, sends the email, and returns True on success.
    
    Args:
        smtp_config (dict): SMTP configuration (host, port, user, password).
        message (MIMEMultipart): The email message to send.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        server = smtplib.SMTP(smtp_config.get('host'), smtp_config.get('port', 587), timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_config.get('user'), smtp_config.get('password'))
        server.send_message(message)
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        raise smtplib.SMTPAuthenticationError(e.smtp_code, e.smtp_error)
    except smtplib.SMTPConnectError as e:
        raise smtplib.SMTPConnectError(e.smtp_code, e.smtp_error)
    except smtplib.SMTPRecipientsRefused as e:
        raise smtplib.SMTPRecipientsRefused(e.recipients)
    except socket.timeout:
        raise TimeoutError("SMTP connection timed out")
    except Exception as e:
        raise e

def send_bulk_emails(smtp_config: Dict[str, Any], recipients: pd.DataFrame, subject: str, template: jinja2.Template, attachments: Optional[List[str]] = None, delay: float = 1.0, logger=None) -> Dict[str, Any]:
    """
    Sends emails to all recipients from a DataFrame with a progress bar and delay.
    
    Args:
        smtp_config (dict): SMTP configuration.
        recipients (pd.DataFrame): DataFrame containing recipient data (must have 'email' column).
        subject (str): The subject of the email.
        template (jinja2.Template): The Jinja2 template for the email body.
        attachments (list[str], optional): List of file paths to attach. Defaults to None.
        delay (float, optional): Delay between emails in seconds. Defaults to 1.0.
        logger (optional): Logger instance. Defaults to None.
        
    Returns:
        dict: A summary containing 'total', 'success', 'failed' counts and 'details' list.
    """
    total = len(recipients)
    success = 0
    failed = 0
    details = []
    
    print(f"Starting bulk email send to {total} recipients...")
    
    # Ensure 'email' column exists, otherwise guess or raise
    email_col = 'email'
    if 'email' not in recipients.columns:
        for col in recipients.columns:
            if 'email' in col.lower():
                email_col = col
                break
        else:
            raise ValueError("DataFrame must contain an 'email' column")
            
    for i, (index, row) in enumerate(recipients.iterrows()):
        recipient_email = row[email_col]
        
        # Context is the entire row as a dictionary
        context = row.to_dict()
        
        try:
            # Render template
            html_body = template.render(**context)
            
            # Get sender details from smtp_config
            sender_email = smtp_config.get('sender_email', smtp_config.get('user'))
            sender_name = smtp_config.get('sender_name', 'Automated Sender')
            
            msg = create_message(
                sender_email=sender_email,
                sender_name=sender_name,
                recipient_email=recipient_email,
                subject=subject,
                html_body=html_body,
                attachments=attachments
            )
            
            # Send email
            send_email(smtp_config, msg)
            
            success += 1
            status = 'success'
            error_msg = ''
            
            # Print progress bar
            progress = int((i + 1) / total * 30)
            bar = f"[{'█' * progress}{'░' * (30 - progress)}] {i + 1}/{total}"
            print(f"  {bar} ✓ Sent to {recipient_email}")
            
        except Exception as e:
            failed += 1
            status = 'failed'
            error_msg = str(e)
            
            # Print progress bar
            progress = int((i + 1) / total * 30)
            bar = f"[{'█' * progress}{'░' * (30 - progress)}] {i + 1}/{total}"
            print(f"  {bar} ✗ Failed: {recipient_email} - {error_msg}")
            
        # Log delivery attempt
        if logger:
            try:
                log_delivery(logger, recipient_email, status, error_msg)
            except Exception as log_e:
                print(f"  Warning: Failed to log delivery for {recipient_email}: {log_e}")
            
        details.append({
            'email': recipient_email,
            'status': status,
            'error': error_msg
        })
        
        # Delay before next email, except for the last one
        if i < total - 1:
            time.sleep(delay)
            
    summary = {
        'total': total,
        'success': success,
        'failed': failed,
        'details': details
    }
    
    print(f"Finished bulk send: {success} successful, {failed} failed out of {total}.")
    
    return summary
