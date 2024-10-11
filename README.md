# YouTube Transcriber

A simple GUI application to download and transcribe YouTube videos.

## Features

- **Download YouTube Videos:** Download audio, video, or both using `yt-dlp`.
- **Transcription:** Transcribe audio using OpenAI's Whisper.
- **User-Friendly GUI:** Built with PySide6 for an intuitive interface.
- **Logging:** Logs application activities for debugging and monitoring.
- **Testing:** Unit tests implemented with `pytest`.

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/youtube_transcriber.git
    cd youtube_transcriber
    ```

2. **Create a Virtual Environment (Optional but Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the application using:

```bash
python main.py
