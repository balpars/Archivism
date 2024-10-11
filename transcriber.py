# transcriber.py

from pathlib import Path
import whisper
import os
import logging
from time import time
import json

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

        transcription = result['text']

        # Create paragraphs based on time gaps
        paragraphs = create_paragraphs_from_segments(result['segments'])

        # Save transcription with paragraphs as .txt
        txt_file = Path(output_folder) / "transcription_with_paragraphs.txt"
        with txt_file.open('w', encoding='utf-8') as f:
            f.write(paragraphs)

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

# Paragraph creation remains unchanged
def create_paragraphs_from_segments(segments, time_gap_threshold=3.0) -> str:
    paragraphs = []
    current_paragraph = []

    for i, segment in enumerate(segments):
        current_paragraph.append(segment['text'])

        if i < len(segments) - 1:
            next_segment_start = segments[i + 1]['start']
            current_segment_end = segment['end']
            time_gap = next_segment_start - current_segment_end

            if time_gap >= time_gap_threshold:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []

    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    return "\n\n".join(paragraphs)

def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
