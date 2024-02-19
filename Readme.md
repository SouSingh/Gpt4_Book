# Project Name

This repository contains a FastAPI server for managing books and providing summaries and audio conversions. Follow the steps below to set up and use the server.

## Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/SouSingh/Gpt4_Book.git
```

### Step 2: Install Dependencies

Navigate to the cloned repository and install the required dependencies using:

change name of .env.example to .env 
put following crediantls

```bash
pip install -r requirements.txt
```

### Step 3: Run FastAPI Server

Run the FastAPI server using the following command:

```bash
uvicorn main:app --host 0.0.0.0 --port 80 --reload
```

## Uploading a Book
To upload a book, follow these steps:

### Step 4: Use Postman to Send POST Request

Download and install Postman. Send a POST request to http://localhost:80/upload with the following form data:

title: Title of the book (e.g., "Tell me now! - 'Good For You'")
author: Author of the book
book_file: Upload the book file of your choice

### Step 5: Receive Response

After sending the POST request, you will receive a response with the paths of the saved book and audio conversion:

```json
{
  "Book_Saved": "assets\\tell-me-now-good-for-you-pratham-FKB.pdf",
  "Audio_Path": "audio\\tell-me-now-good-for-you-pratham-FKB.pdf.mp3"
}
```

The uploaded book and its audio conversion are saved on the server.

## Searching for a Book Summary

To search for a book summary, follow these steps:

### Step 6: Send POST Request for Summary
Send a POST request to http://localhost:80/summary with the following form data:

title: Title of the book (e.g., "Tell me now! - 'Good For You'")

### Step 7: Receive Summary Response

You will receive a response with the paths to the book and audio summary, along with the book summary:

## Example JSON Response

```json
{
  "Book_path": {
    "data": [
      {
        "path": "assets\\tell-me-now-good-for-you-pratham-FKB.pdf"
      }
    ],
    "count": null
  },
  "Audio_summary_path": {
    "data": [
      {
        "Audio": "audio\\tell-me-now-good-for-you-pratham-FKB.pdf.mp3"
      }
    ],
    "count": null
  },
  "Book_Summary": {
    "data": [
      {
        "Summary": "Book_Name: Tell me now! - 'Good For You'\n\nAuthor:\n- Madhav Chavan\n\nSummary:\n- \"Tell me now! - 'Good For You'\" is a children's book that uses a question-and-answer format to teach kids about healthy daily habits and listening to guidance from elders. Topics covered include the importance of regular school attendance, daily bathing, avoiding excessive sun exposure, not staying up late, and getting enough sleep. The book emphasizes that these practices are beneficial for one's well-being. The content is presented in a simple and engaging manner suitable for young readers beginning to read.\n\nTranscription: Tell me now! - 'Good For You'"
      }
    ],
    "count": null
  }
}
```

### step 8: Talk with Rag ai Assistant

Send a POST request to http://127.0.0.1:80/predict with the following form data:

```json
{
    "model": "gpt-4-turbo",
    "response_format": {"type": "json_object"},
    "messages": [
        {
            "role": "system",
            "content": "You are helpful Assistant who is knowldgeable about all PDF and their data inside it",
            "Book_Name": "short-stories-and-other-writings-obooko"
        },
        {
            "role": "user",
            "content": "Which book is written by madhav chavan?"
        }
    ]
}
```

With Book_name which u upload have to same name

Content inside role=>"user" to ask any question about and it will give u LLM response with page number realted to text and text realted

```json
{
  "user_content": {
    "status": "success",
    "message": "Chat completion successful",
    "model_response": [
      {
        "retrieved_chunks": [
          {
            "LLM Response": "The book \"Tell me now! - 'Good For You'\" is written by Madhav Chavan.",
            "Sources": [
              {
                "text": "This story Tell me now! Good For You is written by Madhav Chavan Pratham Books 2004 Some rights reserved Released ",
                "match_score": 0.8,
                "source": "tell-me-now-good-for-you-pratham-FKB.pdf",
                "page_num": "13"
              }
            ],
            "Stats": {
              "percent_display": "100.0%",
              "confirmed_words": [
                "book",
                "tell",
                "now!",
                "'good",
                "you'",
                "written",
                "madhav",
                "chavan"
              ],
              "unconfirmed_words": [],
              "verified_token_match_ratio": 1.0,
              "key_point_list": [
                {
                  "key_point": "The book \"Tell me now! - 'Good For You'\" is written by Madhav Chavan.",
                  "entry": 0,
                  "verified_match": 1.0
                }
              ]
            },
            "Not Found Check": {
              "parse_llm_response": false,
              "evidence_match": true,
              "not_found_classification": false
            }
          }
        ]
      }
    ]
  }
}
```
