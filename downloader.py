import os
import sys
import re
from yt_dlp import YoutubeDL

def sanitize_title(title):
    """
    Sanitizes the title to create a filesystem-friendly folder name.
    """
    # Replace any character that is not alphanumeric, space, or hyphen with an underscore
    sanitized = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces and consecutive underscores with a single underscore
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized.strip('_')

def download_media(url, output_folder, download_format=None):
    """
    Downloads media from the given URL using yt-dlp with restricted filenames.

    Args:
        url (str): The URL of the media or playlist to download.
        output_folder (str): The directory to save the downloaded files.
        download_format (str, optional): Specify the format (e.g., 'best', 'bestaudio', 'bestvideo'). Defaults to 'best'.

    Returns:
        list: List of full paths to the downloaded files.
    """
    # Create the output folder if it doesn't exist
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder, exist_ok=True)

    # Temporary options to extract info without downloading
    ydl_temp_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    with YoutubeDL(ydl_temp_opts) as ydl:
        try:
            # Extract info to get playlist or video title
            info_dict = ydl.extract_info(url, download=False)
            if 'entries' in info_dict:
                # It's a playlist
                playlist_title = info_dict.get('title', 'playlist')
                sanitized_playlist_title = sanitize_title(playlist_title)
                # Create a folder with the sanitized playlist title
                playlist_folder = os.path.join(output_folder, sanitized_playlist_title)
                if not os.path.isdir(playlist_folder):
                    os.makedirs(playlist_folder, exist_ok=True)

                # Process each video in the playlist
                downloaded_files = []
                for entry in info_dict['entries']:
                    if entry is None:
                        continue  # Skip if entry is None
                    video_title = entry.get('title', 'video')
                    sanitized_video_title = sanitize_title(video_title)
                    video_folder = os.path.join(playlist_folder, sanitized_video_title)
                    if not os.path.isdir(video_folder):
                        os.makedirs(video_folder, exist_ok=True)

                    # Set download options for each video
                    ydl_opts = {
                        'restrict_filenames': True,
                        'outtmpl': os.path.join(video_folder, '%(title)s.%(ext)s'),
                        'format': download_format if download_format else 'best',
                        'quiet': True,
                        'no_warnings': True,
                        'skip_download': False,
                    }

                    with YoutubeDL(ydl_opts) as ydl_video:
                        # Download the video
                        video_info = ydl_video.extract_info(entry['webpage_url'], download=True)
                        filename = ydl_video.prepare_filename(video_info)
                        full_path = os.path.abspath(filename)
                        downloaded_files.append(full_path)

                return downloaded_files

            else:
                # It's a single video
                video_title = info_dict.get('title', 'video')
                sanitized_video_title = sanitize_title(video_title)
                video_folder = os.path.join(output_folder, sanitized_video_title)
                if not os.path.isdir(video_folder):
                    os.makedirs(video_folder, exist_ok=True)

                # Set download options
                ydl_opts = {
                    'restrict_filenames': True,
                    'outtmpl': os.path.join(video_folder, '%(title)s.%(ext)s'),
                    'format': download_format if download_format else 'best',
                    'quiet': True,
                    'no_warnings': True,
                }

                with YoutubeDL(ydl_opts) as ydl_video:
                    # Download the video
                    video_info = ydl_video.extract_info(url, download=True)
                    filename = ydl_video.prepare_filename(video_info)
                    full_path = os.path.abspath(filename)

                    return [full_path]

        except Exception as e:
            print(f"Error processing media: {e}", file=sys.stderr)
            sys.exit(1)