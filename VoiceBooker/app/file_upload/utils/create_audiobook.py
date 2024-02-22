from typing import Optional

from app.database.database import Session
from app.database.model import Audiobook
import openai
import os
from openai import OpenAI
import fitz
import pdfplumber
import re
from pathlib import Path
from pydub import AudioSegment



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY


def markdown_to_plain_text(markdown_text):
    # Remove Markdown URL syntax ([text](link)) and keep only the text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown_text)

    # Remove Markdown formatting for bold and italic text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold with **
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic with *
    text = re.sub(r'\_\_([^_]+)\_\_', r'\1', text)  # Bold with __
    text = re.sub(r'\_([^_]+)\_', r'\1', text)      # Italic with _

    # Remove Markdown headers, list items, and blockquote symbols
    text = re.sub(r'#+\s?', '', text)  # Headers
    text = re.sub(r'-\s?', '', text)   # List items
    text = re.sub(r'>\s?', '', text)   # Blockquotes

    return text

def pdf_to_markdown(pdf_path):
    # Open the PDF file at the given path
    with pdfplumber.open(pdf_path) as pdf:
        markdown_content = ""
        # Loop through each page in the PDF
        for page in pdf.pages:
            # Extract text from each page
            text = page.extract_text()
            if text:
                # Format the text with basic Markdown: double newline for new paragraphs
                markdown_page = text.replace('\n', '\n\n')
                # Add a separator line between pages
                markdown_content += markdown_page + '\n\n---\n\n'

        return markdown_content

def split_text(text, max_chunk_size=4096):
    chunks = []  # List to hold the chunks of text
    current_chunk = ""  # String to build the current chunk

    # Split the text into sentences and iterate through them
    for sentence in text.split('.'):
        sentence = sentence.strip()  # Remove leading/trailing whitespaces
        if not sentence:
            continue  # Skip empty sentences

        # Check if adding the sentence would exceed the max chunk size
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += sentence + "."  # Add sentence to current chunk
        else:
            chunks.append(current_chunk)  # Add the current chunk to the list
            current_chunk = sentence + "."  # Start a new chunk

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def text_to_speech(input_text, output_file, model="tts-1-hd", voice="nova"):
    # Initialize the OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Make a request to OpenAI's Audio API with the given text, model, and voice
    response = client.audio.speech.create(
        model=model,      # Model for text-to-speech quality
        voice=voice,      # Voice type
        input=input_text  # The text to be converted into speech
    )

    # Define the path for the output audio file
    speech_file_path = Path(output_file)

    # Stream the audio response to the specified file
    response.stream_to_file(speech_file_path)

    # Print confirmation message after saving the audio file
    print(f"Audio saved to {speech_file_path}")


def convert_chunks_to_audio(chunks, output_folder):
    audio_files = []  # List to store the paths of generated audio files

    # Iterate over each chunk of text
    for i, chunk in enumerate(chunks):
        # Define the path for the output audio file
        output_file = os.path.join(output_folder, f"chunk_{i+1}.mp3")

        # Convert the text chunk to speech and save as an audio file
        text_to_speech(chunk, output_file)

        # Append the path of the created audio file to the list
        audio_files.append(output_file)

    return audio_files

def concatenate_audiobook(directory, name):
    # List all MP3 files in the specified directory
    mp3_files = [file for file in os.listdir(directory) if file.startswith("chunk") and file.endswith(".mp3")]

    # Sort the files to concatenate them in order
    mp3_files.sort()

    # Check if there are any files to process
    if mp3_files:
        # Create an empty AudioSegment to store the combined audio
        combined_audio = AudioSegment.silent(duration=0)

        # Iterate through the MP3 files and concatenate them
        for mp3_file in mp3_files:
            audio_segment = AudioSegment.from_file(os.path.join(directory, mp3_file), format="mp3")
            combined_audio += audio_segment

        # Export the combined audio to a new file
        output_file_path = os.path.join(directory, f"{name}.mp3")
        combined_audio.export(output_file_path, format="mp3")

        for mp3_file in mp3_files:
            if mp3_file.startswith("chunk"):
                os.remove(os.path.join(directory, mp3_file))

        #print(f"Audiobook created and saved to: {output_file_path}")
    else:
        print("No MP3 files found in the specified directory.")

def create_audiobook(
    filename: str,
    ebook_id: int,
    user_id: int,
    session: Session = None,
) -> Audiobook:
    if not session:
        with Session() as session:
            audiobook = create_audiobook(
                filename=filename,
                ebook_id=ebook_id,
                user_id=user_id,
                session=session,
            )
            return audiobook

    di = "./ebooks/" + filename 
    output_folder = "audiobooks"
    markdown_text = pdf_to_markdown(di)
    plain_text = markdown_to_plain_text(markdown_text)
    chunks = split_text(plain_text)
    audio_files = convert_chunks_to_audio(chunks, output_folder)
    concatenate_audiobook(output_folder, filename)
    new_filename = os.path.splitext(filename)[0] + ".mp3"
    audiobook = Audiobook(
        filename=new_filename,
        ebook_id=ebook_id,
        user_id=user_id,
    )

    session.add(audiobook)
    session.commit()
    session.refresh(audiobook)

    return audiobook
