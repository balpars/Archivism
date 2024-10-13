import time
from typing import Optional, List
from pathlib import Path
import yt_dlp
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_video_info(video_url: str, retry_attempts: int = 5, sleep_duration: int = 2) -> Optional[List[dict]]:
    """
    Retrieves the title and duration of the YouTube video or playlist without downloading.
    If the URL is a playlist, returns a list of videos with their title and duration.
    """
    for attempt in range(retry_attempts):
        try:
            ydl_opts = {'quiet': True, 'extract_flat': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                if 'entries' in info:  # Playlist detected
                    videos = []
                    for entry in info['entries']:
                        title = entry.get('title', 'Unknown Title')
                        duration = entry.get('duration', 0)  # Duration in seconds
                        video_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                        videos.append({'title': title, 'duration': duration, 'url': video_url})
                    return videos
                else:  # Single video
                    title = info.get('title', 'Unknown Title')
                    duration = info.get('duration', 0)  # Duration in seconds
                    return [{'title': title, 'duration': duration, 'url': video_url}]
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Error fetching video info on attempt {attempt + 1}/{retry_attempts}: {e}")
            if attempt < retry_attempts - 1:
                time.sleep(sleep_duration)  # Wait for a bit before retrying
            else:
                logging.error(f"Failed to fetch video info after {retry_attempts} attempts.")
                return None


def download_video(video_url: str, output_folder: str = 'output', download_format: str = 'audio',
                   progress_callback=None) -> str:
    """
    Downloads the YouTube video in the specified format (audio or video).
    Returns the actual path to the downloaded file.
    """
    # Ensure output directory exists
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Set up yt-dlp options
    ydl_opts = {
        'outtmpl': str(output_path / '%(title)s-%(id)s.%(ext)s'),  # Save directly to output folder
        'quiet': True,
        'no_warnings': True,
        'restrictfilenames': True,  # Restrict filenames to safe ASCII characters
    }

    # Adding progress callback if available
    if progress_callback:
        def hook(d):
            if d['status'] == 'downloading':
                progress_callback(f"Progress: {d['_percent_str']} Speed: {d['_speed_str']} ETA: {d['eta']}s")

        ydl_opts['progress_hooks'] = [hook]

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
        ydl_opts.update({'format': 'bestvideo+bestaudio/best'})

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if progress_callback:
            progress_callback("Starting download...")

        # Extract video information and download the video
        info_dict = ydl.extract_info(video_url, download=True)

        # Use the actual file path provided by yt-dlp after download
        downloaded_file_path = ydl.prepare_filename(info_dict)

        logging.info(f"Downloaded file: {downloaded_file_path}")
        if progress_callback:
            progress_callback("Download completed.")

        print(downloaded_file_path)

        return str(downloaded_file_path)
