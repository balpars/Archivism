# gui/output_section.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog
from PySide6.QtCore import Signal


class OutputSection(QWidget):
    output_folder_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.output_label = QLabel("Output Folder:")
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select Output Folder (Optional)")
        self.browse_button = QPushButton("Browse")

        layout = QHBoxLayout()
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_path)
        layout.addWidget(self.browse_button)
        self.setLayout(layout)

        self.browse_button.clicked.connect(self.browse_output_folder)
        self.output_path.textChanged.connect(self.emit_output_folder_changed)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_path.setText(folder)

    def emit_output_folder_changed(self):
        self.output_folder_changed.emit(self.output_path.text().strip())

    def get_output_folder(self):
        return self.output_path.text().strip()
