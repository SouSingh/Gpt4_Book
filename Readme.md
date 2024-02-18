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

