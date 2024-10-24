#!/usr/bin/env python3

import os
import argparse
from downloader import download_media
from transcriber import transcribe_audio


def main():
    parser = argparse.ArgumentParser(description="Download videos/audios using yt-dlp with restricted filenames and playlist support.")
    parser.add_argument('url', help='URL of the video or playlist to download')
    parser.add_argument('-o', '--output', default='output', help='Output folder to save the downloaded files (default: output)')
    parser.add_argument('-f', '--format', default='best', help='Format to download (e.g., best, bestaudio, bestvideo)')

    args = parser.parse_args()
    downloaded_files = download_media(args.url, args.output, args.format)   

    print("Downloaded Files:")
    for file_path in downloaded_files:
         print(f"- {file_path}")
         transcribe_audio(file_path, os.path.dirname(file_path))

if __name__ == '__main__':
    main()
