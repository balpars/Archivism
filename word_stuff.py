from docx import Document
from pathlib import Path
import os

def save_transcription_as_word(result, output_folder, file_name, include_timestamps=True):
    """Save transcription as a Word document (.docx)"""
    doc = Document()

    if include_timestamps:
        for segment in result['segments']:
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            doc.add_paragraph(f"{start} --> {end}: {segment['text']}")
    else:
        # Save only the text without timestamps
        for segment in result['segments']:
            doc.add_paragraph(segment['text'])

    output_file = Path(output_folder) / f"{file_name}.docx"
    doc.save(output_file)

def format_timestamp(seconds: float) -> str:
    """Convert seconds to a timestamp (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
