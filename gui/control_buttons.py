# gui/control_buttons.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal


class ControlButtons(QWidget):
    download_clicked = Signal()
    transcribe_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.download_button = QPushButton("Download Only")
        self.transcribe_button = QPushButton("Download and Transcribe")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)

        layout = QHBoxLayout()
        layout.addWidget(self.download_button)
        layout.addWidget(self.transcribe_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        self.download_button.clicked.connect(self.download_clicked.emit)
        self.transcribe_button.clicked.connect(self.transcribe_clicked.emit)
        self.cancel_button.clicked.connect(self.cancel_clicked.emit)

    def enable_buttons(self):
        self.download_button.setEnabled(True)
        self.transcribe_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def disable_buttons(self):
        self.download_button.setEnabled(False)
        self.transcribe_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
