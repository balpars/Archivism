# gui/video_queue.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget


class VideoQueue(QWidget):
    def __init__(self):
        super().__init__()
        self.video_list = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Video Queue:"))
        layout.addWidget(self.video_list)
        self.setLayout(layout)

    def add_video_item(self, title, duration):
        self.video_list.addItem(f"{title} [{duration}]")

    def clear(self):
        self.video_list.clear()
