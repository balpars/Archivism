# utils.py
import os
import logging

def setup_logging(log_file: str = 'logs/app.log'):
    """
    Sets up logging for the application.
    Ensures that multiple handlers are not added.
    """
    if not logging.getLogger().hasHandlers():
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] [%(filename)s:%(funcName)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

