import os
import subprocess
import sys
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QListWidget, QRadioButton,
                             QButtonGroup, QFileDialog, QMessageBox)
from controller import WorkerThread


class VideoTranscriberGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.video_list = []  # List for URLs
        self.local_file_list = []  # List for local files
        self.output_path = os.path.join(os.path.dirname(__file__), "output")
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Archivism")
        self.setGeometry(100, 100, 700, 600)

        # Set macOS-like style
        self.setStyleSheet("""
            QWidget {
                background-color: #F0F0F0;
                font-family: 'Helvetica Neue', Arial, sans-serif;
            }

            QLabel {
                color: #333;
                font-size: 12px;

            }

            QLineEdit {
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                selection-background-color: #D5E1E6;
                selection-color: #333;
            }

            QPushButton {
                width: 80px;  /* Set desired width */
                height: 20px;  /* Set desired height */
                padding: 5px;  /* Padding inside buttons (increases button size) */
                margin: 5px;    /* Margin around buttons (space between buttons) */
                background-color: #0078D7;  /* Background color */
                color: white;  /* Text color */
                border: none;  /* No border */
                border-radius: 5px;  /* Rounded corners */
                font-size: 14px;  /* Font size */
            }

            QPushButton:hover {
                background-color: #005BB5;
            }

            QListWidget {
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
            }

            QRadioButton {
                font-size: 14px;
                padding: 5px;
            }
        """)

        # Main Layout
        layout = QVBoxLayout()

        # Mode Selection
        mode_layout = QHBoxLayout()
        self.download_radio = QRadioButton("Download Only")
        self.download_transcribe_radio = QRadioButton("Download | Transcribe")
        mode_group = QButtonGroup()
        mode_group.addButton(self.download_radio)
        mode_group.addButton(self.download_transcribe_radio)
        self.download_transcribe_radio.setChecked(True)

        mode_layout.addWidget(self.download_radio)
        mode_layout.addWidget(self.download_transcribe_radio)
        layout.addLayout(mode_layout)

        # URL Input Section
        url_layout = QHBoxLayout()
        url_label = QLabel("Video URL:")
        self.url_input = QLineEdit()
        self.url_input.setFixedWidth(550)
        self.add_url_button = QPushButton("Add URL")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.add_url_button)
        layout.addLayout(url_layout)

        # File Selection for URL List
        file_layout = QHBoxLayout()
        file_label = QLabel("URL File:")
        self.file_path_input = QLineEdit()
        self.file_path_input.setFixedWidth(550)
        self.browse_file_button = QPushButton("Browse")
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(self.browse_file_button)
        layout.addLayout(file_layout)

        # Media Folder Selection
        media_folder_layout = QHBoxLayout()
        media_folder_label = QLabel("Media Folder:")
        self.media_folder_input = QLineEdit()
        self.media_folder_input.setFixedWidth(550)
        self.browse_media_folder_button = QPushButton("Browse")
        media_folder_layout.addWidget(media_folder_label)
        media_folder_layout.addWidget(self.media_folder_input)
        media_folder_layout.addWidget(self.browse_media_folder_button)
        layout.addLayout(media_folder_layout)

        # Single Media File Selection
        single_media_layout = QHBoxLayout()
        single_media_label = QLabel("Single File:")
        self.single_media_input = QLineEdit()
        self.single_media_input.setFixedWidth(550)
        self.browse_single_media_button = QPushButton("Browse")
        single_media_layout.addWidget(single_media_label)
        single_media_layout.addWidget(self.single_media_input)
        single_media_layout.addWidget(self.browse_single_media_button)
        layout.addLayout(single_media_layout)

        # URL List Display
        video_list_label = QLabel("Video URL List:")
        self.video_list_box = QListWidget()
        layout.addWidget(video_list_label)
        layout.addWidget(self.video_list_box)

        # Local Files List Display
        local_file_list_label = QLabel("Local File List:")
        self.local_file_list_box = QListWidget()
        layout.addWidget(local_file_list_label)
        layout.addWidget(self.local_file_list_box)


        # Current action label
        self.current_action_label = QLabel("")
        layout.addWidget(self.current_action_label)

        # Start Button
        self.start_button = QPushButton("Start Process")
        layout.addWidget(self.start_button)

        # Set layout
        self.setLayout(layout)

        # Connect buttons
        self.browse_file_button.clicked.connect(self.browse_url_file)
        self.add_url_button.clicked.connect(self.add_url)
        self.browse_media_folder_button.clicked.connect(self.browse_media_folder)
        self.browse_single_media_button.clicked.connect(self.browse_single_media_file)
        self.start_button.clicked.connect(self.start_process)

        # Connect mode selection signals to update UI
        self.download_radio.toggled.connect(self.update_ui_for_mode)
        self.download_transcribe_radio.toggled.connect(self.update_ui_for_mode)

        # Initialize UI state
        self.update_ui_for_mode()

    def update_ui_for_mode(self):
        """Update UI elements based on the selected mode."""
        if self.download_radio.isChecked():
            self.set_ui_state(url_enabled=True, media_folder_enabled=False, single_file_enabled=False)
            self.start_button.setText("Download Video")

        elif self.download_transcribe_radio.isChecked():
            self.set_ui_state(url_enabled=True, media_folder_enabled=True, single_file_enabled=True)
            self.start_button.setText("Download | Transcribe Video")

    def set_ui_state(self, url_enabled, media_folder_enabled, single_file_enabled):
        """Helper to enable/disable UI elements based on mode."""
        # URL section
        self.url_input.setEnabled(url_enabled)
        self.add_url_button.setEnabled(url_enabled)
        self.file_path_input.setEnabled(url_enabled)
        self.browse_file_button.setEnabled(url_enabled)

        # Media folder section
        self.media_folder_input.setEnabled(media_folder_enabled)
        self.browse_media_folder_button.setEnabled(media_folder_enabled)

        # Single media file section
        self.single_media_input.setEnabled(single_file_enabled)
        self.browse_single_media_button.setEnabled(single_file_enabled)


    def browse_url_file(self):
        """Open a file dialog to select a URL file."""
        self.file_path_input.clear()
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select URL File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            self.file_path_input.setText(file_path)
            self.load_urls_from_file(file_path)

    def browse_media_folder(self):
        """Open a dialog to select a folder containing media files and add valid media files to the list."""
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "Select Media Folder", options=options)

        if folder_path:
            self.media_folder_input.setText(folder_path)

            # Define allowed media file extensions
            allowed_extensions = {".mp4", ".mkv", ".avi", ".mov", ".mp3", ".m4a"}

            # Loop through files in the selected folder
            for filename in os.listdir(folder_path):
                media_file_path = os.path.join(folder_path, filename)
                # Check if it's a file and has an allowed extension
                if os.path.isfile(media_file_path) and os.path.splitext(filename)[1].lower() in allowed_extensions:
                    # Add the media file path to the list and update the display
                    self.local_file_list.append(media_file_path)
                    self.local_file_list_box.addItem(media_file_path)

    def browse_single_media_file(self):
        """Open a file dialog to select a single media file for transcription."""
        options = QFileDialog.Options()
        media_file_path, _ = QFileDialog.getOpenFileName(self, "Select Media File", "", "Media Files (*.mp4 *.mkv *.avi *.mov *.mp3 *.m4a);;All Files (*)", options=options)
        if media_file_path:
            self.single_media_input.setText(media_file_path)
            self.local_file_list.append(media_file_path)
            self.local_file_list_box.addItem(media_file_path)

    def add_url(self):
        """Add the URL from the input field to the video list."""
        url = self.url_input.text().strip()
        if url:
            if url not in self.video_list:
                self.video_list.append(url)
                self.video_list_box.addItem(url)
                self.url_input.clear()
            else:
                QMessageBox.warning(self, "Input Error", "URL already in list")

    def load_urls_from_file(self, file_path):
        """Load URLs from a specified file and add them to the video list."""
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    url = line.strip()
                    if url:
                        self.video_list.append(url)
                        self.video_list_box.addItem(url)
        except Exception as e:
            print(f"Error reading file: {e}")

    def update_action_label(self, text):
        """Update the current action label."""
        self.current_action_label.setText(text)

    def start_process(self):
        """Start the video processing based on the selected mode."""
        if not self.video_list and not self.local_file_list:
            QMessageBox.warning(self, "Input Error", "No video to process")
        else:
            self.update_action_label("Starting process...")
            self.start_button.setEnabled(False)
            self.worker = WorkerThread(self.video_list, self.local_file_list, self.output_path,
                                       self.download_radio.isChecked())
            self.worker.update_label.connect(self.update_action_label)
            self.worker.process_finished.connect(self.on_process_finished)
            self.worker.start()

    def on_process_finished(self):
        """Called when the process is finished."""
        self.update_action_label("Process finished!")
        self.video_list.clear()
        self.local_file_list.clear()
        self.video_list_box.clear()
        self.local_file_list_box.clear()
        self.start_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = VideoTranscriberGUI()
    gui.show()
    sys.exit(app.exec_())
