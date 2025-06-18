# logging_config.py
# Configures logging for DocQuery Agent, including file-based logs and optional email alerts for errors.
# Used by backend modules to log uploads, classifications, user actions, and errors.

import logging
import os
from logging.handlers import SMTPHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILES = {
    'upload': os.path.join(LOG_DIR, 'upload.log'),
    'classification': os.path.join(LOG_DIR, 'classification.log'),
    'errors': os.path.join(LOG_DIR, 'errors.log'),
    'user_actions': os.path.join(LOG_DIR, 'user_actions.log'),
}

# Email alert configuration (update with your real credentials)
MAIL_HOST = 'smtp.example.com'
MAIL_PORT = 587
MAIL_USERNAME = 'your_email@example.com'
MAIL_PASSWORD = 'your_password'
MAIL_FROM = 'your_email@example.com'
MAIL_TO = ['recipient@example.com']


def get_logger(name, log_type):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILES[log_type])
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        if log_type == 'errors':
            logger.setLevel(logging.ERROR)
            # Add SMTPHandler for error logger
            mail_handler = SMTPHandler(
                mailhost=(MAIL_HOST, MAIL_PORT),
                fromaddr=MAIL_FROM,
                toaddrs=MAIL_TO,
                subject='[DocQuery Agent] System Error Alert',
                credentials=(MAIL_USERNAME, MAIL_PASSWORD),
                secure=()
            )
            mail_handler.setLevel(logging.ERROR)
            mail_handler.setFormatter(formatter)
            logger.addHandler(mail_handler)
        else:
            logger.setLevel(logging.INFO)
    return logger
