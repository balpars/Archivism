# gui/main_window.py

import sys
import json
import uuid
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QApplication
import logging
from pathlib import Path
from utils import setup_logging, create_output_folder, sanitize_filename
from gui.input_section import InputSection
from gui.video_queue import VideoQueue
from gui.output_section import OutputSection
from gui.settings_section import SettingsSection
from gui.control_buttons import ControlButtons
from gui.status_bar import StatusBar
from gui.threads import DownloadThread, TranscribeThread
from downloader import get_video_info
from time import time

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Transcriber")
        self.setMinimumSize(800, 600)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Instance attributes
        self.video_queue = []
        self.current_thread = None
        self.file_mapping = {}  # Maps UUID to file info
        self.metadata_file = "file_metadata.json"

        # Set up UI components
        self.input_section = InputSection()
        self.video_queue_widget = VideoQueue()
        self.output_section = OutputSection()
        self.settings_section = SettingsSection()
        self.control_buttons = ControlButtons()
        self.status_bar = StatusBar()

        # Assemble UI components
        self.layout.addWidget(self.input_section)
        self.layout.addWidget(self.video_queue_widget)
        self.layout.addWidget(self.output_section)
        self.layout.addWidget(self.settings_section)
        self.layout.addWidget(self.control_buttons)
        self.layout.addWidget(self.status_bar)

        # Connect signals
        self.input_section.add_url.connect(self.add_url)
        self.input_section.add_local_file.connect(self.add_local_files)
        self.control_buttons.download_clicked.connect(self.download_only)
        self.control_buttons.transcribe_clicked.connect(self.download_and_transcribe)
        self.control_buttons.cancel_clicked.connect(self.cancel_operation)

        # Load metadata
        self.load_metadata()

        # Set up logging
        setup_logging()

    def load_metadata(self):
        """Load metadata from JSON file to retain state across sessions."""
        try:
            with open(self.metadata_file, "r") as file:
                self.file_mapping = json.load(file)
        except FileNotFoundError:
            self.file_mapping = {}

    def save_metadata(self):
        """Save metadata to JSON file."""
        with open(self.metadata_file, "w") as file:
            json.dump(self.file_mapping, file)

    def add_url(self, url):
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a valid YouTube URL.")
            return

        video_info = get_video_info(url)
        if video_info:
            title = video_info['title']
            duration = self.format_duration(video_info['duration'])
            unique_id = str(uuid.uuid4())
            sanitized_title = sanitize_filename(title)
            output_folder = create_output_folder(sanitized_title)

            self.video_queue.append(unique_id)
            self.file_mapping[unique_id] = {
                'source': url,
                'original_name': title,
                'sanitized_name': sanitized_title,
                'output_folder': output_folder,
                'duration': duration
            }

            self.video_queue_widget.add_video_item(title, duration)
            logging.info(f"Added URL to queue: {url} with title: {title}")

            # Save metadata
            self.save_metadata()
        else:
            QMessageBox.critical(self, "Error", "Failed to retrieve video info.")

    def add_local_files(self):
        from PySide6.QtWidgets import QFileDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Select Audio/Video Files", "", "Audio/Video Files (*.mp4 *.mkv *.mp3 *.wav)")
        for file in files:
            unique_id = str(uuid.uuid4())
            filename = Path(file).name
            sanitized_filename = sanitize_filename(filename)
            output_folder = create_output_folder(sanitized_filename)

            # Add to mapping
            self.file_mapping[unique_id] = {
                'source': file,
                'original_name': filename,
                'sanitized_name': sanitized_filename,
                'output_folder': output_folder,
                'duration': self.get_local_file_duration(file)
            }

            # Add to queue
            self.video_queue.append(unique_id)
            self.video_queue_widget.add_video_item(filename, self.file_mapping[unique_id]['duration'])
            logging.info(f"Added local file to queue: {file}")

            # Save metadata
            self.save_metadata()

    def download_only(self):
        if not self.video_queue:
            QMessageBox.warning(self, "Queue Empty", "Please add videos to the queue.")
            return

        self.process_videos(transcribe=False)

    def download_and_transcribe(self):
        if not self.video_queue:
            QMessageBox.warning(self, "Queue Empty", "Please add videos to the queue.")
            return

        self.process_videos(transcribe=True)

    def cancel_operation(self):
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.stop()  # Use stop() to gracefully terminate the thread
            self.current_thread.wait()
            self.current_thread = None
            self.status_bar.set_status("Operation cancelled.")
            self.control_buttons.enable_buttons()

    def process_videos(self, transcribe=False):
        self.control_buttons.disable_buttons()
        self.status_bar.set_progress(0, maximum=len(self.video_queue))
        self.status_bar.set_status("Processing videos...")

        self.current_index = 0
        self.transcribe = transcribe

        self.process_next_video()

    def process_next_video(self):
        if self.current_index >= len(self.video_queue):
            self.status_bar.set_status("All operations completed.")
            QMessageBox.information(self, "Success", "All operations completed successfully.")
            self.reset_ui()
            return

        unique_id = self.video_queue[self.current_index]
        video_info = self.file_mapping[unique_id]
        source = video_info['source']
        sanitized_name = video_info['sanitized_name']
        video_output_folder = video_info['output_folder']

        if Path(source).exists():
            # Local file
            if self.transcribe:
                self.start_transcription(source, video_output_folder)
            else:
                self.current_index += 1
                self.status_bar.set_progress(self.current_index)
                self.process_next_video()
        else:
            # URL, start download
            self.current_thread = DownloadThread(
                source,
                video_output_folder,
                self.settings_section.get_download_format()
            )
            self.current_thread.progress.connect(self.update_status)
            self.current_thread.finished.connect(lambda file_path, id=unique_id: self.on_download_finished(file_path, id))
            self.current_thread.error.connect(self.on_error)
            self.current_thread.start()

    def on_download_finished(self, file_path, unique_id):
        # Update file path in the metadata after download
        self.file_mapping[unique_id]['downloaded_path'] = file_path

        # Once the download finishes, start transcription if needed
        if self.transcribe:
            self.start_transcription(file_path, Path(file_path).parent)
        else:
            self.current_index += 1
            self.status_bar.set_progress(self.current_index)
            self.process_next_video()

    def start_transcription(self, file_path, output_folder):
        self.current_thread = TranscribeThread(
            file_path,
            output_folder,
            language=self.settings_section.get_language(),
            model_size=self.settings_section.get_model_size()
        )
        self.current_thread.progress.connect(self.update_status)
        self.current_thread.finished.connect(self.on_transcription_finished)
        self.current_thread.error.connect(self.on_error)
        self.current_thread.start()

    def on_transcription_finished(self, duration):
        self.current_index += 1
        self.status_bar.set_progress(self.current_index)
        self.process_next_video()

    def update_status(self, message):
        self.status_bar.set_status(message)
        logging.info(message)

    def on_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        logging.error(f"Error: {error_message}")
        self.reset_ui()

    def reset_ui(self):
        self.control_buttons.enable_buttons()
        self.current_thread = None
        self.video_queue.clear()
        self.video_queue_widget.clear()
        self.status_bar.reset()

    def format_duration(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{int(minutes)}:{int(seconds):02d}"

    def get_local_file_duration(self, file_path):
        return "Unknown"  # Placeholder for duration retrieval logic


# The rest of your files would be adapted accordingly as follows:
