# VoiceBooker

## Build Setup
1. Clone the repository
    ```bash
    git clone git@github.com:SoSaymon/VoiceBooker.git
    ```
2. create a virtual environment and activate it
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install the requirements
    ```bash
    pip install -r requirements.txt
    ```
4. Run the server
    ```bash
    uvicorn app.main:app
    ```
   

## API Documentation
### File Upload
- **http://localhost:8000/upload-ebook**
    - **Method**: POST
    - **Request**: 
        - **Headers**: 
            - Content-Type: multipart/form-data
            - Authorization: Bearer `<token>`
        - **Body**: 
            - file: `<file>`
            - title: `<Book name of file>`
            - author: `<author of book file>`
    - **Response**: 
        - **Status Code**: 200
          - **Body**: 
              - filename: `<filename>`
              - file_type: `<file_type>`
              - email: `<email>`
- **http://localhost:8000/get-audiobook/{filename}**
    - **Method**: GET
    - **Request**: 
        - **Headers**: 
            - Authorization Bearer `<token>`
        - **Body**: 
            - None
    - **Response**:
    - **Status Code**: 200
        - **Body**: 
            - `<audiobook>`
            - **Headers**: 
                - Content-Disposition: attachment; filename=`<filename>`
                - Content-Type: audio/mpeg



## File Upload

### How to upload a file
1. Send file via POST `/upload-ebook` endpoint
2. You will receive a response with the filename, file_type and email
3. Use the filename amd file_type to add the `FileUpload` via GrapQL mutation (see below)
    ```grqaphql
   mutation createFileUpload($filename: String!, $fileType: String!, $title: String!, $author: String!, $summary: String!) {
    createFileUpload(filename: $filename, fileType: $fileType, title: $title, author: $author, summary: $summary) {
        ok
        fileUpload {
            id
            filename
            fileType
            userId
            createdAt
            deleteTime
            user {
                username
            }
            ebooks {
                id
                title
                author
                summary
            }
        }
    }
    }
    ```

### How to get the audiobook

1. Send a request via GQL `GetAudiobookFilename` query
    ```graphql
    query getAudiobookFilename($ebookId: Int!) {
    getAudiobookFilename(ebookId: $ebookId)
    }
    ```
2. You will receive a response with the filename
3. Use the filename to send a GET request to `/get-audiobook` endpoint
4. You will receive the audiobook file