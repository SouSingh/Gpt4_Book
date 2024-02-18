from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import os
from supabase import create_client
from dotenv import load_dotenv
from supabase import Client, create_client
from llama_index.llms.clarifai import Clarifai
import fitz  # PyMuPDF
from pathlib import Path
from openai import OpenAI

def convert_pdf_to_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text += page.get_text()
    return text


app = FastAPI()


load_dotenv()

# Supabase configuration
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
os.environ["CLARIFAI_PAT"] = os.getenv("CLARIFAI_PAT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
cllient = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(url, key)


assets_folder = "assets"
speech_folder = "audio"
os.makedirs(assets_folder, exist_ok=True)
os.makedirs(speech_folder, exist_ok=True)

@app.post("/upload")
async def upload_book(
    title: str = Form(...),
    author: str = Form(...),
    book_file: UploadFile = File(...),
):
    # Save the book file to the assets folder
    file_path = os.path.join(assets_folder, book_file.filename)
    with open(file_path, "wb") as file:
        file.write(book_file.file.read())

    # Store information in Supabase
    dat = convert_pdf_to_text(file_path)
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

            Transcription: {dat}
            ''')
    summary = (str(summary))
    response = cllient.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=f"{summary}"
        )
    speech_file_path = os.path.join(speech_folder, book_file.filename)
    if not speech_file_path.lower().endswith('.mp3'):
        speech_file_path += '.mp3'
    response.stream_to_file(speech_file_path)
    response = supabase.table("Books").insert({"title": title, "author": author, "path": file_path, "Summary": summary,"Audio":speech_file_path}).execute()
    re = {
        "Book_Saved": file_path,
        "Audio_Path": speech_file_path
    }
    return re

@app.post("/summary")
async def get_summary(
    title: str = Form(...)):
    response_summary = supabase.table("Books").select('Summary').eq('title',title).execute()
    response_path = supabase.table("Books").select('path').eq('title',title).execute()
    response_audio = supabase.table("Books").select('Audio').eq('title',title).execute()
    data = {
        "Book_path": response_path,
        "Audio_summary_path": response_audio,
        "Book_Summary": response_summary
    }
    return data





