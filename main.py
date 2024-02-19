from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
import os
from supabase import create_client
from dotenv import load_dotenv
from supabase import Client, create_client
from llama_index.llms.clarifai import Clarifai
from llmware.prompts import Prompt
from llmware.configs import LLMWareConfig
import fitz  # PyMuPDF
from pathlib import Path
import openai

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
#cllient = OpenAI(api_key=OPENAI_API_KEY)
supabase: Client = create_client(url, key)


assets_folder = "assets"
speech_folder = "audio"
os.makedirs(assets_folder, exist_ok=True)
os.makedirs(speech_folder, exist_ok=True)


def contract_analysis_w_fact_checking(text, topic):
    if not text:
        raise HTTPException(status_code=400, detail="Text field is required in the input data.")

    contracts_path = "./assets"
    contract = topic + ".pdf"

    # create prompt object
    prompter = Prompt().load_model("gpt-4", api_key=os.getenv('OPENAI_API_KEY'), from_hf=False)

    research = {"topic": "Books", "prompt": f"{text}"}

    # Results will be stored in this list
    results = []
    print("Question: ", research["prompt"])
    source = prompter.add_source_document(contracts_path, contract, query=research["topic"])
    responses = prompter.prompt_with_source(research["prompt"], prompt_name="just_the_facts", temperature=0.3)
    ev_numbers = prompter.evidence_check_numbers(responses)
    ev_sources = prompter.evidence_check_sources(responses)
    ev_stats = prompter.evidence_comparison_stats(responses)
    z = prompter.classify_not_found_response(responses, parse_response=True, evidence_match=True, ask_the_model=False)

    contract_results = []

    for r, response in enumerate(responses):
            contract_results.append({
                "LLM Response": response["llm_response"],
                "Sources": [{
                    "text": source["text"],
                    "match_score": source["match_score"],
                    "source": source["source"],
                    "page_num": source.get("page_num", None)
                } for source in ev_sources[r]["source_review"]],
                "Stats": {
                    "percent_display": ev_stats[r]["comparison_stats"]["percent_display"],
                    "confirmed_words": ev_stats[r]["comparison_stats"]["confirmed_words"],
                    "unconfirmed_words": ev_stats[r]["comparison_stats"]["unconfirmed_words"],
                    "verified_token_match_ratio": ev_stats[r]["comparison_stats"]["verified_token_match_ratio"],
                    "key_point_list": [{
                        "key_point": key_point["key_point"],
                        "entry": key_point["entry"],
                        "verified_match": key_point["verified_match"]
                    } for key_point in ev_stats[r]["comparison_stats"]["key_point_list"]]
                },
                "Not Found Check": {
                    "parse_llm_response": False,
                    "evidence_match": True,
                    "not_found_classification": z[r]["not_found_classification"]
                }
            })

    results.append({
            "retrieved_chunks": contract_results
    })

    prompter.clear_source_materials()

    print("\nupdate: prompt state saved at: ", os.path.join(LLMWareConfig.get_prompt_path(), prompter.prompt_id))
    prompter.save_state()

    return {"status": "success", "message": "Chat completion successful", "model_response": results}

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
    response = openai.audio.speech.create(
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


@app.post("/predict")
async def predict(data: dict):
    try:
        messages = data.get("messages", [])
        user_message = next((msg["content"] for msg in messages if msg["role"] == "user"), None)
        user_topic = next((msg["Book_Name"] for msg in messages if msg["role"] == "system"), None)
        out = contract_analysis_w_fact_checking(user_message, user_topic)
        if user_message:
            return {"user_content": out}
        else:
            raise HTTPException(status_code=400, detail="User message not found in input.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




