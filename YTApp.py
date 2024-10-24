import sys
import os
import torch
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal
from downloader import download_media
from transcriber import transcribe_audio
from yt_dlp import YoutubeDL


def get_device():
    """Utility function to set the device to GPU if available, else CPU."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return device


def get_video_names(url: str):
    """Returns a list of video names from the provided URL."""
    ydl_opts = {'quiet': True}  # Suppress console output from yt-dlp
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            video_names = []

            # If it's a playlist, get all video names
            if 'entries' in info_dict:
                video_names = [(entry['id'], entry['title']) for entry in info_dict['entries']]
            else:
                # Single video, add title to list
                video_names.append((info_dict['id'], info_dict['title']))

            return video_names

        except Exception as e:
            print(f"Error checking URL: {e}")
            return [(None, f"Error: {e}")]  # Return a tuple with None for URL


class NameCheckWorker(QThread):
    video_names_ready = pyqtSignal(list)  # Signal to emit when names are ready

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        """Run the get_video_names function in the background."""
        video_names = get_video_names(self.url)
        self.video_names_ready.emit(video_names)


class Worker(QThread):
    progress = pyqtSignal(str)

    def __init__(self, urls, output_folder):
        super().__init__()
        self.urls = urls
        self.output_folder = output_folder

    def run(self):
        """Perform the downloading and transcribing in the background."""
        for url in self.urls:
            self.progress.emit(f"Downloading: {url}")
            downloaded_files = download_media(url, self.output_folder, 'best')

            for file_path in downloaded_files:
                self.progress.emit(f"Transcribing: {os.path.basename(file_path)}")
                transcribe_audio(file_path, os.path.dirname(file_path))

        self.progress.emit("Completed all downloads and transcriptions.")


class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.device = get_device()  # Set the device
        self.update_device_label()  # Update the label based on the device

    def initUI(self):
        # Main window layout
        layout = QVBoxLayout()

        # Device info layout
        self.device_label = QLabel("")
        layout.addWidget(self.device_label)

        # URL input layout
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter video/playlist URL")
        url_layout.addWidget(QLabel("URL:"))
        url_layout.addWidget(self.url_input)
        self.add_url_button = QPushButton("Add URL", self)
        self.add_url_button.clicked.connect(self.check_url)
        url_layout.addWidget(self.add_url_button)

        # Output folder layout
        output_layout = QHBoxLayout()
        self.output_folder_input = QLineEdit(self)
        self.output_folder_input.setPlaceholderText("Select output folder")
        output_layout.addWidget(QLabel("Output Folder:"))
        output_layout.addWidget(self.output_folder_input)
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.browse_button)

        # Queued URLs list
        self.url_list = QListWidget(self)

        # Start download button
        self.start_button = QPushButton("Start Download", self)
        self.start_button.clicked.connect(self.start_download)

        # Status label
        self.status_label = QLabel("")

        # Adding layouts to the main layout
        layout.addLayout(url_layout)
        layout.addLayout(output_layout)
        layout.addWidget(QLabel("Queued Videos:"))
        layout.addWidget(self.url_list)
        layout.addWidget(self.start_button)
        layout.addWidget(self.status_label)

        # Set layout to the window
        self.setLayout(layout)
        self.setWindowTitle('Media Downloader & Transcriber')
        self.setGeometry(300, 300, 600, 400)

        # URL queue
        self.urls = []  # Store URLs for downloading
        self.titles = []  # Store titles for display
        self.worker = None

    def update_device_label(self):
        """Update the device label to inform the user about CPU/GPU usage."""
        if self.device.type == 'cuda':
            self.device_label.setText("Using GPU for processing.")
        else:
            self.device_label.setText("Using CPU for processing. This may take longer.")
            self.status_label.setText("Warning: CUDA GPU is recommended for faster processing.")

    def check_url(self):
        """Check the URL to see if it's a playlist or video, and get names asynchronously."""
        url = self.url_input.text().strip()
        if url:
            self.status_label.setText("Checking URL...")
            self.name_check_worker = NameCheckWorker(url)
            self.name_check_worker.video_names_ready.connect(self.process_video_names)
            self.name_check_worker.start()

    def process_video_names(self, video_names):
        """Process the video names when the worker is done."""
        if len(video_names) > 1:
            self.status_label.setText(f"Playlist detected: {len(video_names)} videos")
        else:
            self.status_label.setText("Single video detected")

        # Add all video names and their corresponding URLs to the queue
        for video_id, title in video_names:
            self.url_list.addItem(title)
            self.urls.append(video_id)  # Use video ID as URL for downloading

        # Clear URL input
        self.url_input.clear()

    def browse_output_folder(self):
        """Open a file dialog to select the output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder_input.setText(folder)

    def start_download(self):
        """Start downloading and transcribing videos in a separate thread."""
        if not self.urls:
            self.status_label.setText("No URLs to process.")
            return

        output_folder = self.output_folder_input.text() or 'output'

        # Disable the start button while processing
        self.start_button.setEnabled(False)
        self.status_label.setText("Starting download...")

        # Create a worker thread for downloading and transcribing
        self.worker = Worker(self.urls, output_folder)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()

    def update_status(self, message):
        """Update the status label with progress."""
        self.status_label.setText(message)

    def processing_finished(self):
        """Re-enable the start button and clear the URL queue."""
        self.start_button.setEnabled(True)
        self.urls.clear()
        self.titles.clear()
        self.url_list.clear()
        self.status_label.setText("Processing completed!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec_())
