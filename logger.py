import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

class ColoredConsoleHandler(logging.StreamHandler):
    """A custom logging handler that adds color to console output based on level."""
    def emit(self, record):
        colors = {
            logging.DEBUG: '\033[94m',    # Blue
            logging.INFO: '\033[92m',     # Green
            logging.WARNING: '\033[93m',  # Yellow
            logging.ERROR: '\033[91m',    # Red
            logging.CRITICAL: '\033[1;91m'# Bold Red
        }
        reset = '\033[0m'
        
        # Apply color based on log level
        color = colors.get(record.levelno, reset)
        msg = self.format(record)
        
        self.stream.write(f"{color}{msg}{reset}\n")
        self.flush()

def setup_logger(log_dir: str = 'logs') -> logging.Logger:
    """
    Sets up logging for the application.
    Logs to both console (colored INFO) and a rotating file (DEBUG) in logs/.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger('email_automation')
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding multiple handlers if setup is called multiple times
    if logger.handlers:
        return logger

    # Date-based filename for rotating file handler
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_filename = os.path.join(log_dir, f"email_log_{date_str}.log")

    # File Handler: 5MB max size, 5 backup files
    file_handler = RotatingFileHandler(
        log_filename, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Console Handler: Colored output, INFO level
    console_handler = ColoredConsoleHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def log_delivery(logger: logging.Logger, recipient_email: str, status: str, message: str = ''):
    """
    Convenience function to log delivery status (SUCCESS/FAILED).
    """
    log_msg = f"Delivery to {recipient_email}: {status.upper()}"
    if message:
        log_msg += f" - {message}"
        
    if status.upper() == 'SUCCESS':
        logger.info(log_msg)
    else:
        logger.error(log_msg)
