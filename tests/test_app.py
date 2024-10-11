import pytest
from downloader.yt_dlp_downloader import YtDlpDownloader

def test_yt_dlp_downloader():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Sample URL
    downloader = YtDlpDownloader(url, download_video=False)
    downloader.run()
    assert downloader.output_path is not None
