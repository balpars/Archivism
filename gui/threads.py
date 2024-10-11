# gui/threads.py

from PySide6.QtCore import QThread, Signal
import logging
from downloader import download_video
from transcriber import transcribe_audio

class DownloadThread(QThread):
    progress = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, video_url, output_folder, download_format):
        super().__init__()
        self.video_url = video_url
        self.output_folder = output_folder
        self.download_format = download_format
        self._should_stop = False  # Graceful stop flag

    def run(self):
        try:
            logging.info(f"Starting download: {self.video_url}")
            self.progress.emit("Starting download...")
            file_path = download_video(self.video_url, self.output_folder, self.download_format, self.progress_callback)
            if self._should_stop:
                logging.info("Download stopped by user.")
                return
            self.finished.emit(file_path)
            logging.info(f"Download finished: {file_path}")
        except Exception as e:
            logging.error(f"Error downloading: {e}")
            self.error.emit(str(e))

    def progress_callback(self, message):
        if self._should_stop:
            logging.info("Download stopped by user.")
            return
        self.progress.emit(message)

    def stop(self):
        self._should_stop = True

class TranscribeThread(QThread):
    progress = Signal(str)
    finished = Signal(float)
    error = Signal(str)

    def __init__(self, file_path, output_folder, language, model_size):
        super().__init__()
        self.file_path = file_path
        self.output_folder = output_folder
        self.language = language
        self.model_size = model_size
        self._should_stop = False  # Graceful stop flag

    def run(self):
        try:
            logging.info(f"Starting transcription: {self.file_path}")
            self.progress.emit("Starting transcription...")
            duration = transcribe_audio(
                self.file_path,
                self.output_folder,
                language=self.language,
                model_size=self.model_size,
                progress_callback=self.progress_callback
            )
            if self._should_stop:
                logging.info("Transcription stopped by user.")
                return
            self.finished.emit(duration)
            logging.info("Transcription completed.")
        except Exception as e:
            logging.error(f"Transcription error: {e}")
            self.error.emit(str(e))

    def progress_callback(self, message):
        if self._should_stop:
            logging.info("Transcription stopped by user.")
            return
        self.progress.emit(message)

    def stop(self):
        self._should_stop = True
