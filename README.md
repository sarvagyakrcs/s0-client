# S0: AI-Powered Component Generator
<img src="https://raw.githubusercontent.com/sarvagyakrcs/s0-client/refs/heads/main/demo/Create%20Next%20App.jpeg" />
    
"Bridging the gap between design inspiration and implementation through AI-powered component generation."

## Overview
The **Component Search API** is a FastAPI-based application that enables users to search for code components and generate UI components using machine learning models. The API leverages **CodeBERT** and **BERT** for embedding generation and **Gemini AI** for component generation. The backend is powered by a PostgreSQL database hosted on NeonDB.

## Features
- **Search Components**: Find relevant code components based on a query.
- **Generate Components**: Generate HTML/JSX/TSX components based on input query and similar components.
- **Health Check**: Verify if the API is running correctly.

## Technologies Used
- **FastAPI** - API framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL (NeonDB)** - Database storage
- **Hugging Face Transformers** - Machine learning models (CodeBERT, BERT)
- **Gemini AI** - Text generation for UI components

---

## API Endpoints

### 1. Health Check
#### **Endpoint:** `/health`
#### **Method:** `GET`
#### **Description:**
Checks if the API is running.
#### **Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. Search Components
#### **Endpoint:** `/search`
#### **Method:** `POST`
#### **Request Body:**
```json
{
  "query": "string",
  "limit": 10
}
```
#### **Response:**
```json
{
  "code_matches": [
    {
      "id": "string",
      "title": "string",
      "summary": "string",
      "code_snippet": "string",
      "similarity_score": 0.95
    }
  ],
  "summary_matches": [
    {
      "id": "string",
      "title": "string",
      "summary": "string",
      "code_snippet": "string",
      "similarity_score": 0.90
    }
  ]
}
```

---

### 3. Generate Component
#### **Endpoint:** `/generate`
#### **Method:** `POST`
#### **Request Body:**
```json
{
  "query": "string",
  "output_format": "html | jsx-js | jsx-ts",
  "similar_count": 3
}
```
#### **Response:**
```json
{
  "generated_code": "string",
  "similar_components": [
    {
      "id": "string",
      "title": "string",
      "summary": "string",
      "code_snippet": "string",
      "similarity_score": 0.85
    }
  ],
  "explanation": "string"
}
```

---

## Database Schema
### Table: `code_components`
| Column Name        | Type     | Description                          |
|--------------------|---------|--------------------------------------|
| `id`              | `UUID`  | Unique identifier                    |
| `title`           | `TEXT`  | Component title                      |
| `summary`         | `TEXT`  | Component summary                    |
| `code_snippet`    | `TEXT`  | Code snippet of the component        |
| `code_embedding`  | `VECTOR`| CodeBERT-generated embedding         |
| `summary_embedding` | `VECTOR` | BERT-generated embedding           |

---

## Embedding Functions

### **1. Get Code Embedding**
#### **Function:** `get_code_embedding(text: str) -> List[float]`
#### **Description:**
Generates a CodeBERT embedding vector for a given code snippet.

### **2. Get Summary Embedding**
#### **Function:** `get_summary_embedding(text: str) -> List[float]`
#### **Description:**
Generates a BERT embedding vector for a given summary.

---

## AI Model Configuration
### **Gemini AI Configuration**
```python
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
```

### **Safety Settings**
```python
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}
```

---

## Deployment & Running Instructions
### **1. Environment Setup**
- Install dependencies:
  ```sh
  pip install fastapi uvicorn torch transformers sqlalchemy psycopg2 dotenv google-generativeai
  ```
- Set environment variables:
  ```sh
  export API_KEY="your_gemini_api_key"
  export DATABASE_URL="your_database_url"
  ```

### **2. Running the API**
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Error Handling
| Error Code | Description                         |
|------------|-------------------------------------|
| 400        | Bad Request (Invalid input)        |
| 500        | Internal Server Error              |
| 503        | Service Unavailable (AI failure)   |

---

## Future Improvements
- Add authentication and API rate limiting.
- Improve AI-generated component accuracy.
- Expand support for more programming languages.

---

## License
MIT License

---

## Contact
For questions or support, reach out to `dev@yourdomain.com`.

