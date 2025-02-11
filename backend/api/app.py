from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModel
from sqlalchemy import create_engine, text
import numpy as np
from typing import List, Dict
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import re
from enum import Enum

# Load environment variables
load_dotenv()

app = FastAPI(title="Component Search API")

# Database connection
DATABASE_URL = "postgresql://neondb_owner:npg_GcEiX10HoVvO@ep-morning-shadow-a17ijyhw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)

# Load models
code_tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
code_model = AutoModel.from_pretrained('microsoft/codebert-base')
summary_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
summary_model = AutoModel.from_pretrained('bert-base-uncased')

# Replace Groq initialization with Gemini
genai.configure(api_key="AIzaSyCLmLTy4xlbDW65tyLLIhCMY74qCp3Uq9Q")

# Configure Gemini
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Initialize Gemini model
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Test the model connection
try:
    response = model.generate_content("test")
    print("Successfully connected to Gemini AI")
except Exception as e:
    print(f"Warning: Failed to connect to Gemini AI: {str(e)}")

class SearchResult(BaseModel):
    id: str
    title: str
    summary: str
    code_snippet: str
    similarity_score: float

class SearchResponse(BaseModel):
    code_matches: List[SearchResult]
    summary_matches: List[SearchResult]

# Add request model
class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class OutputFormat(Enum):
    HTML = "html"
    JSX_JS = "jsx-js"
    JSX_TS = "jsx-ts"

class GenerateRequest(BaseModel):
    query: str
    output_format: OutputFormat = OutputFormat.HTML
    similar_count: int = 3

class GenerateResponse(BaseModel):
    generated_code: str
    similar_components: List[SearchResult]
    explanation: str

def get_code_embedding(text: str) -> List[float]:
    """Generate CodeBERT embedding for code snippet."""
    try:
        inputs = code_tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = code_model(**inputs)
        return outputs.last_hidden_state[0][0].numpy().tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code embedding: {str(e)}")

def get_summary_embedding(text: str) -> List[float]:
    """Generate BERT embedding for summary text."""
    try:
        inputs = summary_tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = summary_model(**inputs)
        return outputs.last_hidden_state[0][0].numpy().tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary embedding: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search_components(request: SearchRequest):
    """
    Search for similar components using both code and summary embeddings.
    """
    try:
        # Generate embeddings for the query
        code_embedding = get_code_embedding(request.query)
        summary_embedding = get_summary_embedding(request.query)
        
        # Convert embeddings to PostgreSQL array format
        code_vector = f"[{','.join(map(str, code_embedding))}]"
        summary_vector = f"[{','.join(map(str, summary_embedding))}]"
        
        # Updated SQL query with direct vector casting
        code_query = text(f"""
            SELECT id, title, summary, code_snippet, 
                1 - (code_embedding <-> '{code_vector}') as similarity
            FROM code_components
            ORDER BY code_embedding <-> '{code_vector}'
            LIMIT :limit
        """)

        summary_query = text(f"""
            SELECT id, title, summary, code_snippet,
                1 - (summary_embedding <-> '{summary_vector}') as similarity
            FROM code_components
            ORDER BY summary_embedding <-> '{summary_vector}'
            LIMIT :limit
        """)

        
        with engine.connect() as conn:
            # Execute queries with vector parameters
            code_results = conn.execute(
                code_query,
                {
                    "code_vector": code_vector,
                    "limit": request.limit
                }
            ).fetchall()
            
            summary_results = conn.execute(
                summary_query,
                {
                    "summary_vector": summary_vector,
                    "limit": request.limit
                }
            ).fetchall()
        
        # Format results
        code_matches = [
            SearchResult(
                id=str(row[0]),
                title=str(row[1]),
                summary=str(row[2]),
                code_snippet=str(row[3]),
                similarity_score=float(row[4])
            )
            for row in code_results
        ]
        
        summary_matches = [
            SearchResult(
                id=str(row[0]),
                title=str(row[1]),
                summary=str(row[2]),
                code_snippet=str(row[3]),
                similarity_score=float(row[4])
            )
            for row in summary_results
        ]

        
        
        return SearchResponse(
            code_matches=code_matches,
            summary_matches=summary_matches
        )
        
    except Exception as e:
        print(f"Search error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/generate", response_model=GenerateResponse)
async def generate_component(request: GenerateRequest):
    """
    Generate a component based on query and similar examples.
    Supports HTML, JSX (JavaScript), and JSX (TypeScript) output formats.
    """
    try:
        if not model:
            raise HTTPException(
                status_code=503,
                detail="Gemini AI model is not initialized"
            )

        # First get similar components
        search_request = SearchRequest(query=request.query, limit=request.similar_count)
        search_results = await search_components(search_request)
        examples = search_results.code_matches[:request.similar_count]

        # Create format-specific instructions
        format_instructions = {
            OutputFormat.HTML: """
Format the component as semantic HTML5 with CSS classes.
Example:
<div class="component">
  <!-- Component content -->
</div>
""",
            OutputFormat.JSX_JS: """
Format the component as a React JSX component using JavaScript.
Example:
const Component = ({ props }) => {
  return (
    <div className="component">
      {/* Component content */}
    </div>
  );
};
export default Component;
""",
            OutputFormat.JSX_TS: """
Format the component as a React JSX component using TypeScript.
Example:
interface ComponentProps {
  // Define props here
}

const Component: React.FC<ComponentProps> = ({ props }) => {
  return (
    <div className="component">
      {/* Component content */}
    </div>
  );
};
export default Component;
"""
        }

        # Create prompt with examples and format instructions
        example_text = "\n\n".join([
            f"Example {i+1}:\n```\n{example.code_snippet}\n```"
            for i, example in enumerate(examples)
        ])

        prompt = f"""Create a UI component based on this request: {request.query}

Here are similar components for reference:
{example_text}

{format_instructions[request.output_format]}

Requirements:
1. Follow best practices for {request.output_format.value}
2. Make it accessible (ARIA attributes where needed)
3. Make it responsive
4. Include comments explaining key parts
5. Use semantic elements/components

Return your response in this exact format:
<COMPONENT>
[Your code here]
</COMPONENT>

<EXPLANATION>
[Brief explanation of the component, its features, and usage]
</EXPLANATION>
"""

        # Generate response using Gemini
        response = model.generate_content(prompt)
        response_text = response.text

        # Extract code and explanation
        code_match = re.search(r'<COMPONENT>\s*(.*?)\s*</COMPONENT>', response_text, re.DOTALL)
        explanation_match = re.search(r'<EXPLANATION>\s*(.*?)\s*</EXPLANATION>', response_text, re.DOTALL)

        if not code_match or not explanation_match:
            raise ValueError("Failed to parse generated response")

        return GenerateResponse(
            generated_code=code_match.group(1).strip(),
            similar_components=examples,
            explanation=explanation_match.group(1).strip()
        )

    except Exception as e:
        print(f"Generation error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 