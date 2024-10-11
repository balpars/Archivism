# utils.py
import os
import re
import logging
from datetime import datetime
import unicodedata

def sanitize_filename(filename: str) -> str:
    """
    Removes invalid characters from filenames.
    """
    safe_filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    safe_filename = unicodedata.normalize('NFKD', safe_filename).encode('ascii', 'ignore').decode('utf-8')  # Normalize international characters
    safe_filename = safe_filename.strip()
    return safe_filename

def create_output_folder(title: str, parent_folder: str = 'output') -> str:
    """
    Creates an output folder based on the title and the current date.
    """
    safe_title = sanitize_filename(title)
    current_date = datetime.now().strftime("%Y-%m-%d")
    folder_base = f"{safe_title}_{current_date}"
    folder_path = os.path.join(parent_folder, folder_base)

    # Ensure folder uniqueness
    counter = 1
    original_folder_path = folder_path
    while os.path.exists(folder_path):
        folder_path = f"{original_folder_path}_{counter}"
        counter += 1

    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def setup_logging(log_file: str = 'logs/app.log'):
    """
    Sets up logging for the application.
    Ensures that multiple handlers are not added.
    """
    if not logging.getLogger().hasHandlers():
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
