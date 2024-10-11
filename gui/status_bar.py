# gui/status_bar.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar


class StatusBar(QWidget):
    def __init__(self):
        super().__init__()
        self.status_label = QLabel("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def set_status(self, message):
        self.status_label.setText(message)

    def set_progress(self, value, maximum=None):
        if maximum is not None:
            self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)

    def reset(self):
        self.status_label.setText("Ready")
        self.progress_bar.setValue(0)
