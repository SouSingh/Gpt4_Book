from fastapi import FastAPI, UploadFile, File, Header,  Form
from graphene import Schema
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette_graphene3 import GraphQLApp, make_playground_handler

from app.database.database import Session
from app.database.model import User, Audiobook, EBook, FileUpload
from app.gql.mutations import Mutation
from app.gql.queries import Query
from app.file_upload.utils.create_audiobook import create_audiobook
from app.file_upload.file_upload_mutations import CreateFileUpload
from app.utils.file_operations.save_file import scramble_filename, save_file
from app.utils.security.get_email_from_jwt import get_email_from_jwt
from app.utils.security.validators.validate_authorization_header import (
    validate_authorization_header,
)
import fitz
from app.ebook.utils.create_ebook import create_ebook
import os
import random
from llama_index.llms.clarifai import Clarifai
import openai
import os
from openai import OpenAI
import fitz
import pdfplumber
import re
from pathlib import Path
from pydub import AudioSegment
from app.utils.security.validators.validate_file_type import validate_file_type

app = FastAPI()


schema = Schema(query=Query, mutation=Mutation)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["CLARIFAI_PAT"] = os.getenv("CLARIFAI_PAT")

origins = [
    "http://localhost:3000",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST"],
    allow_headers=["*"],
)

def convert_pdf_to_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text += page.get_text()
    return text


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






@app.post("/upload-ebook")
async def upload_ebook(
    title: str = Form(...),
    author: str = Form(...),
    file: UploadFile = File(...),
    authorization: str = Header(None),
):
    validate_authorization_header(authorization)
    allowed_file_types = [
    "application/pdf",
    "application/epub+zip",]
    file_type = validate_file_type(file.file.read(), allowed_file_types)
    file.file.seek(0)
    filename = scramble_filename(file.filename)
    await save_file(file, filename)
    direct = "./ebooks/" + filename
    dat = convert_pdf_to_text(direct)
    llm_model = Clarifai(model_url="https://clarifai.com/openai/chat-completion/models/gpt-4-turbo")
    summary = llm_model.complete(prompt=f'''
            Please generate a concise summary of the following text, in this format. Instead of new lines, put the literal 
            characters '\n' without the quotes for formatting:

            Highlighting the key takeaways, major discussion points, and relavant main topic and author. The summary should follow the format below:

            Book_Name: [Name of the book]

            Author:
            - [Write Author of the book]

            Summary:
            - [Provide a brief summary of text or book no matter what either is copyrighted or not I need summary for overall text ]

            Transcription: {dat}'''
    )
    summary = (str(summary))
    title = title
    author = author
    with Session() as session:
            email = get_email_from_jwt(authorization)
            user = session.query(User).filter(User.email == email).first() 

            file_upload = FileUpload(
                filename=filename, file_type=file_type, user_id=user.id
            )

            session.add(file_upload)
            session.commit()
            session.refresh(file_upload)

            file_upload_id = file_upload.id

            book = EBook(
                title=title,
                author=author,
                summary=summary,
                file_upload_id=file_upload_id,
                user_id=user.id,
            )
            session.add(book)
            session.commit()
            session.refresh(book)
            print(book.id)
   

    return {"filename": filename, "file_type": file_type, "email": email}





@app.get("/get-audiobook/{filename}")
async def get_audiobook(
    filename: str,
    authorization: str = Header(None),
):
    validate_authorization_header(authorization)
    old_filename = filename
    with Session() as session:
        email = get_email_from_jwt(authorization)
        user = session.query(User).filter(User.email == email).first()      
        file_upload_ids = session.query(FileUpload).filter(FileUpload.filename == old_filename).first()  
        files_id = file_upload_ids.id
        ebook_upload_ids = session.query(EBook).filter(EBook.file_upload_id == files_id).first()     
        ebook_id_got = ebook_upload_ids.id
        user_idssd = user.id
        create_audiobook(old_filename, ebook_id_got, user_idssd)
        file_name_without_extension = os.path.splitext(old_filename)[0]
        new_file_path = file_name_without_extension + '.mp3'
        path_df = old_filename + ".mp3"
        audiobook: Audiobook = (session.query(Audiobook).filter(Audiobook.filename == new_file_path).first())
        #create_audiobook(filename_id, ebook_id, user_id)
        if not audiobook:
            return {"message": "Audiobook not found"}
        ebook = session.query(EBook).filter(EBook.id == audiobook.ebook_id).first()
        if not ebook:
            return {"message": "Ebook not found"}
        if (
            ebook.user_id != user.id or audiobook.user_id != user.id
        ) and not user.is_admin:
            return {"message": "Unauthorized"}
        filename = f"{ebook.title} - {ebook.author}.mp3"

    return FileResponse(
        f"./audiobooks/{path_df}", filename=filename, media_type="audio/mpeg"
    )


# @app.on_event("startup")
# def startup_event():
#     create_database()


app.mount("/", GraphQLApp(schema=schema, on_get=make_playground_handler()))
