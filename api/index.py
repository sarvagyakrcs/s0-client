"""
Main application entry point.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from enum import Enum
import re
import torch
from transformers import AutoTokenizer, AutoModel
from sqlalchemy import create_engine, text
import logging
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="S0: UI Component Generation")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = "postgresql://neondb_owner:npg_YKfst1aPuq9Q@ep-morning-shadow-a17ijyhw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)

# Load embedding models
code_tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
code_model = AutoModel.from_pretrained('microsoft/codebert-base')
summary_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
summary_model = AutoModel.from_pretrained('bert-base-uncased')

# Configure Groq with Deepseek model
client = Groq(
    api_key="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"
)

class OutputFormat(str, Enum):
    HTML = "html"
    JSX_JS = "jsx-js"
    JSX_TS = "jsx-ts"

class SimilarComponent(BaseModel):
    id: str
    title: str
    summary: str
    code_snippet: str
    similarity_score: float

class GenerateRequest(BaseModel):
    query: str
    output_format: OutputFormat
    similar_count: int = 5

class GenerateResponse(BaseModel):
    """Response model with optional generated code."""
    generated_code: str | None = None
    explanation: str | None = None
    similar_components: List[SimilarComponent]
    error: str | None = None

def get_code_embedding(text: str) -> List[float]:
    """Generate CodeBERT embedding for code snippet."""
    try:
        logger.info("Generating CodeBERT embedding")
        inputs = code_tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = code_model(**inputs)
        embedding = outputs.last_hidden_state[0][0].numpy().tolist()
        logger.info("Successfully generated CodeBERT embedding")
        return embedding
    except Exception as e:
        logger.error(f"Error generating code embedding: {str(e)}")
        raise

def get_summary_embedding(text: str) -> List[float]:
    """Generate BERT embedding for summary text."""
    inputs = summary_tokenizer(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
    with torch.no_grad():
        outputs = summary_model(**inputs)
    return outputs.last_hidden_state[0][0].numpy().tolist()

async def generate_with_deepseek(prompt: str) -> str:
    """Generate text using Deepseek via Groq."""
    try:
        logger.info("Sending request to Deepseek")
        messages = [
            {
                "role": "system",
                "content": "You are an expert UI component developer specializing in React, TypeScript, and modern web development."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=messages,
            temperature=0.6,
            max_completion_tokens=4096,
            top_p=0.95,
            stream=True,
            stop=None
        )

        # Combine streaming response
        response_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content

        logger.info("Received response from Deepseek")
        return response_text

    except Exception as e:
        logger.error(f"Deepseek generation error: {str(e)}")
        raise

def get_similar_components(query: str, limit: int = 5) -> List[SimilarComponent]:
    """Get similar components using both code and summary embeddings."""
    try:
        logger.info(f"Finding similar components for query: {query}, limit: {limit}")
        
        # Get half the requested components from each embedding type
        per_type_limit = (limit + 1) // 2  # Round up for odd numbers
        
        code_embedding = get_code_embedding(query)
        summary_embedding = get_summary_embedding(query)
        
        code_vector = f"[{','.join(map(str, code_embedding))}]"
        summary_vector = f"[{','.join(map(str, summary_embedding))}]"
        
        with engine.connect() as conn:
            code_results = conn.execute(
                text(f"""
                    SELECT id, title, summary, code_snippet, 
                        1 - (code_embedding <-> '{code_vector}') as similarity
                    FROM code_components
                    ORDER BY code_embedding <-> '{code_vector}'
                    LIMIT :limit
                """),
                {"limit": per_type_limit}
            ).fetchall()
            
            summary_results = conn.execute(
                text(f"""
                    SELECT id, title, summary, code_snippet,
                        1 - (summary_embedding <-> '{summary_vector}') as similarity
                    FROM code_components
                    ORDER BY summary_embedding <-> '{summary_vector}'
                    LIMIT :limit
                """),
                {"limit": per_type_limit}
            ).fetchall()
        
        # Combine and deduplicate results
        similar_components = []
        seen_ids = set()
        
        for row in code_results + summary_results:
            if row[0] not in seen_ids and len(similar_components) < limit:
                seen_ids.add(row[0])
                similar_components.append(
                    SimilarComponent(
                        id=str(row[0]),
                        title=str(row[1]),
                        summary=str(row[2]),
                        code_snippet=str(row[3]),
                        similarity_score=float(row[4])
                    )
                )
        
        logger.info(f"Returning {len(similar_components)} unique similar components")
        return similar_components
        
    except Exception as e:
        logger.error(f"Error finding similar components: {str(e)}")
        raise

@app.post("/generate", response_model=GenerateResponse)
async def generate_component(request: GenerateRequest):
    """Generate a component based on query and similar examples."""
    try:
        logger.info(f"Received generation request: {request.query}")
        
        # Get 10 similar components (5 from each embedding type)
        similar_components = get_similar_components(request.query, limit=5)
        logger.info(f"Found {len(similar_components)} similar components")

        try:
            # Create examples text for LLM
            examples_text = "\n\n".join([
                f"Example {i+1} ({component.title}):\n```\n{component.code_snippet}\n```"
                for i, component in enumerate(similar_components[:4])  # Use only top 4 for LLM
            ])
            
            format_instructions = {
                OutputFormat.HTML: "Create a semantic HTML5 component with CSS classes",
                OutputFormat.JSX_JS: "Create a React functional component using JavaScript",
                OutputFormat.JSX_TS: "Create a React functional component using TypeScript"
            }

            prompt = f"""Create a {request.output_format} component for: {request.query}

Reference components:
{examples_text}

Requirements:
- Format: {format_instructions[request.output_format]}
- Make it accessible (ARIA)
- Make it responsive
- Add clear comments
- Follow best practices

Return in this format:
<COMPONENT>
[Your code here]
</COMPONENT>

<EXPLANATION>
[Brief explanation]
</EXPLANATION>
"""
            
            # Generate using Deepseek
            response_text = await generate_with_deepseek(prompt)
            
            # Parse response
            code_match = re.search(r'<COMPONENT>\s*(.*?)\s*</COMPONENT>', response_text, re.DOTALL)
            explanation_match = re.search(r'<EXPLANATION>\s*(.*?)\s*</EXPLANATION>', response_text, re.DOTALL)
            
            if not code_match or not explanation_match:
                logger.error("Failed to parse Deepseek response")
                logger.error(f"Response text: {response_text}")
                return GenerateResponse(
                    error="Failed to generate component, but found similar components",
                    similar_components=similar_components
                )
                
            logger.info("Successfully parsed response")
            return GenerateResponse(
                generated_code=code_match.group(1).strip(),
                explanation=explanation_match.group(1).strip(),
                similar_components=similar_components
            )

        except Exception as e:
            logger.error(f"LLM generation error: {str(e)}")
            # Return similar components even if LLM fails
            return GenerateResponse(
                error=f"Component generation failed: {str(e)}",
                similar_components=similar_components
            )

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        logger.error(f"Full error details: {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 