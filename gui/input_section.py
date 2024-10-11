# gui/input_section.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Signal


class InputSection(QWidget):
    add_url = Signal(str)
    add_local_file = Signal()

    def __init__(self):
        super().__init__()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL")
        self.add_url_button = QPushButton("Add URL")
        self.add_local_file_button = QPushButton("Add Local File")

        layout = QHBoxLayout()
        layout.addWidget(self.url_input)
        layout.addWidget(self.add_url_button)
        layout.addWidget(self.add_local_file_button)
        self.setLayout(layout)

        # Connect signals
        self.add_url_button.clicked.connect(self.emit_add_url)
        self.add_local_file_button.clicked.connect(self.add_local_file.emit)

    def emit_add_url(self):
        url = self.url_input.text().strip()
        self.add_url.emit(url)
        self.url_input.clear()
