# gui/settings_section.py

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QRadioButton, QComboBox, QFormLayout


class SettingsSection(QWidget):
    def __init__(self):
        super().__init__()
        # Download Format
        self.format_label = QLabel("Download Format:")
        self.audio_radio = QRadioButton("Audio Only")
        self.video_radio = QRadioButton("Video Only")
        self.audio_radio.setChecked(True)
        format_layout = QHBoxLayout()
        format_layout.addWidget(self.audio_radio)
        format_layout.addWidget(self.video_radio)

        # Whisper Model
        self.model_label = QLabel("Whisper Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large", "turbo"])
        self.model_combo.setCurrentText("turbo")

        # Language
        self.language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Auto Detect", "English", "Turkish"])
        self.language_combo.setCurrentText("Auto Detect")

        settings_layout = QFormLayout()
        settings_layout.addRow(self.format_label, format_layout)
        settings_layout.addRow(self.model_label, self.model_combo)
        settings_layout.addRow(self.language_label, self.language_combo)

        self.setLayout(settings_layout)

    def get_download_format(self):
        return 'audio' if self.audio_radio.isChecked() else 'video'

    def get_model_size(self):
        return self.model_combo.currentText()

    def get_language(self):
        language = self.language_combo.currentText()
        return None if language == "Auto Detect" else language.lower()
