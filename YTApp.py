import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal
from downloader import download_media
from transcriber import transcribe_audio


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

    def initUI(self):
        # Main window layout
        layout = QVBoxLayout()

        # URL input layout
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter video/playlist URL")
        url_layout.addWidget(QLabel("URL:"))
        url_layout.addWidget(self.url_input)
        self.add_url_button = QPushButton("Add URL", self)
        self.add_url_button.clicked.connect(self.add_url)
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
        layout.addWidget(QLabel("Queued URLs:"))
        layout.addWidget(self.url_list)
        layout.addWidget(self.start_button)
        layout.addWidget(self.status_label)

        # Set layout to the window
        self.setLayout(layout)
        self.setWindowTitle('Media Downloader & Transcriber')
        self.setGeometry(300, 300, 600, 400)

        # URL queue
        self.urls = []
        self.worker = None

    def add_url(self):
        """Add URL to the queue."""
        url = self.url_input.text().strip()
        if url:
            self.urls.append(url)
            self.url_list.addItem(url)
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
        self.url_list.clear()
        self.status_label.setText("Processing completed!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec_())
