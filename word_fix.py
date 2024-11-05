import os
import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from docx import Document


class NewlineRemoverGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Word Fixer")
        self.setGeometry(100, 100, 600, 100)

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
                width: 80px;
                height: 20px;
                padding: 5px;
                margin: 5px;
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005BB5;
            }
        """)

        # Main layout
        layout = QVBoxLayout()

        # File selection layout
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Select File:")
        self.file_path_input = QLineEdit()
        self.file_path_input.setFixedWidth(450)
        self.browse_button = QPushButton("Browse")
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)

        # Process file button
        self.process_button = QPushButton("Process and Save")
        layout.addWidget(self.process_button)

        # Current action label
        self.current_action_label = QLabel("")
        layout.addWidget(self.current_action_label)

        self.setLayout(layout)

        # Connect buttons
        self.browse_button.clicked.connect(self.select_file)
        self.process_button.clicked.connect(self.process_file)

        # Initialize file path
        self.file_path = None

    def select_file(self):
        # Open file dialog to select .docx or .txt file
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Text Files (*.txt);;Word Documents (*.docx)", options=options
        )

        if file_path:
            self.file_path = file_path
            self.file_path_input.setText(file_path)
            self.current_action_label.setText(f"Selected File: {file_path}")

    def process_file(self):
        if not self.file_path:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return

        try:
            # Read the file content based on its type
            if self.file_path.endswith('.txt'):
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            elif self.file_path.endswith('.docx'):
                doc = Document(self.file_path)
                text = "\n".join([para.text for para in doc.paragraphs])

            # Process text to remove newlines within sentences
            patched_text = self.replace_newlines_in_sentence(text)

            # Save the result to a new text file
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Save File", "", "Text Files (*.txt)", options=QFileDialog.Options()
            )
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as file:
                    file.write(patched_text)
                self.current_action_label.setText(f"File saved to: {save_path}")
                QMessageBox.information(self, "Success", f"File saved to: {save_path}")
            else:
                self.current_action_label.setText("Save operation was cancelled.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def replace_newlines_in_sentence(self, text):
        # Replace newline characters not preceded by a period, question mark, or exclamation point with a space
        return re.sub(r'(?<![.!?])\n', ' ', text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = NewlineRemoverGUI()
    gui.show()
    sys.exit(app.exec_())
