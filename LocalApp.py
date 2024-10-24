import sys
import torch
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QLineEdit
)
from PyQt5.QtCore import QThread, pyqtSignal
from transcriber import transcribe_audio  # Ensure this function supports CUDA


def get_device():
    """Utility function to set the device to GPU if available, else CPU."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return device


class Worker(QThread):
    progress = pyqtSignal(str)

    def __init__(self, files, output_folder, device):
        super().__init__()
        self.files = files
        self.output_folder = output_folder
        self.device = device

    def run(self):
        """Perform the file processing in the background."""
        for file_path in self.files:
            self.progress.emit(f"Processing: {os.path.basename(file_path)}")
            transcribe_audio(file_path, self.output_folder)
        self.progress.emit("Completed all files.")


class LocalFileApp(QWidget):
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

        # File selection layout
        file_layout = QHBoxLayout()
        self.add_file_button = QPushButton("Add Files", self)
        self.add_file_button.clicked.connect(self.add_files)
        file_layout.addWidget(self.add_file_button)

        # Output folder layout
        output_layout = QHBoxLayout()
        self.output_folder_input = QLineEdit(self)
        self.output_folder_input.setPlaceholderText("Select output folder")
        output_layout.addWidget(QLabel("Output Folder:"))
        output_layout.addWidget(self.output_folder_input)
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.browse_button)

        # Queued files list
        self.file_list = QListWidget(self)

        # Start processing button
        self.start_button = QPushButton("Start Processing", self)
        self.start_button.clicked.connect(self.start_processing)

        # Status label
        self.status_label = QLabel("")

        # Adding layouts to the main layout
        layout.addLayout(file_layout)
        layout.addLayout(output_layout)
        layout.addWidget(QLabel("Queued Files:"))
        layout.addWidget(self.file_list)
        layout.addWidget(self.start_button)
        layout.addWidget(self.status_label)

        # Set layout to the window
        self.setLayout(layout)
        self.setWindowTitle('Local File Processor & Transcriber')
        self.setGeometry(300, 300, 600, 400)

        # File queue
        self.files = []
        self.worker = None

    def update_device_label(self):
        """Update the device label to inform the user about CPU/GPU usage."""
        if self.device.type == 'cuda':
            self.device_label.setText("Using GPU for processing.")
        else:
            self.device_label.setText("Using CPU for processing. This may take longer.")
            self.status_label.setText("Warning: CUDA GPU is recommended for faster processing.")

    def add_files(self):
        """Add local files to the queue and set output folder to the video file's directory."""
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if file_paths:
            self.files.extend(file_paths)
            self.file_list.addItems(file_paths)

            # Set the output folder to the directory of the first selected file
            first_file_directory = os.path.dirname(file_paths[0])
            self.output_folder_input.setText(first_file_directory)

    def browse_output_folder(self):
        """Open a file dialog to select the output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder_input.setText(folder)

    def start_processing(self):
        """Start processing and transcribing local files in a separate thread."""
        if not self.files:
            self.status_label.setText("No files to process.")
            return

        output_folder = self.output_folder_input.text() or 'output'

        # Disable the start button while processing
        self.start_button.setEnabled(False)
        self.status_label.setText("Processing files...")

        # Create a worker thread for file processing
        self.worker = Worker(self.files, output_folder, self.device)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()

    def update_status(self, message):
        """Update the status label with progress."""
        self.status_label.setText(message)

    def processing_finished(self):
        """Re-enable the start button and clear the file queue."""
        self.start_button.setEnabled(True)
        self.files.clear()
        self.file_list.clear()
        self.status_label.setText("Processing completed!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LocalFileApp()
    window.show()
    sys.exit(app.exec_())
