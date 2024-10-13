# transcriber.py
from pathlib import Path
import whisper
import os
import logging
from time import time


# Cache Whisper model to avoid loading multiple times
model_cache = {}

def load_whisper_model(model_size: str):
    if model_size not in model_cache:
        logging.info(f"Loading Whisper model '{model_size}'...")
        model_cache[model_size] = whisper.load_model(model_size)
    return model_cache[model_size]

def transcribe_audio(file_path: str, output_folder: str, language: str = None, model_size: str = 'base', progress_callback=None) -> float:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if progress_callback:
            progress_callback("Loading Whisper model...")

        model = load_whisper_model(model_size)

        start_time = time()

        if progress_callback:
            progress_callback("Transcribing audio...")

        logging.info(f"Transcribing audio: {file_path}...")
        result = model.transcribe(file_path, language=language)

        # Save transcription as .srt
        srt_file = Path(output_folder) / "transcription.srt"
        with srt_file.open('w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments']):
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                f.write(f"{i + 1}\n{start} --> {end}\n{segment['text']}\n\n")

        logging.info(f"Transcription saved in {output_folder}")

        end_time = time()
        duration = end_time - start_time
        logging.info(f"Transcription took {duration:.2f} seconds.")

        return duration

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise e
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        raise e


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
