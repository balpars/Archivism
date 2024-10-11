# downloader.py
from pathlib import Path
from typing import Optional

import yt_dlp
import os
import logging
from utils import sanitize_filename

def download_video(video_url: str, output_folder: str, download_format: str = 'audio', progress_callback=None) -> str:
    """
    Downloads the YouTube video in the specified format (audio or video).
    Returns the actual path to the downloaded file.
    """
    ydl_opts = {
        'outtmpl': str(Path(output_folder) / '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [],  # To capture the final file path
    }

    # Determine the desired format
    if download_format == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({'format': 'bestvideo+bestaudio'})

    # Container to capture the downloaded file path
    downloaded_file = []

    def my_hook(d):
        if d['status'] == 'finished':
            # Capture the final file path after all post-processing
            downloaded_file.append(Path(d['info_dict']['filepath']))

    ydl_opts['progress_hooks'].append(my_hook)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            if progress_callback:
                progress_callback("Starting download...")
            ydl.extract_info(video_url, download=True)

            if not downloaded_file:
                logging.error("No file was downloaded.")
                raise FileNotFoundError("No file was downloaded.")

            actual_file_path = downloaded_file[0]
            logging.info(f"Downloaded file: {actual_file_path}")

            if progress_callback:
                progress_callback("Download completed.")

            return str(actual_file_path)  # Return the actual file path as string

        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            raise e


def get_video_info(video_url: str) -> Optional[dict]:
    """
    Retrieves the title and duration of the YouTube video without downloading it.
    """
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'Unknown Title')
            duration = info.get('duration', 0)  # Duration in seconds
            return {'title': title, 'duration': duration}
    except Exception as e:
        logging.error(f"Error fetching video info: {e}")
        return None
