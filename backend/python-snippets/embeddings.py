import json
import torch
from transformers import AutoTokenizer, AutoModel
from sqlalchemy import create_engine, Column, String, Text, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
import numpy as np
from typing import List, Dict
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize GROQ client
groq_client = Groq(api_key="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")

# Database setup
DATABASE_URL = "postgresql://neondb_owner:npg_LkgS8BGKhw9c@ep-morning-shadow-a17ijyhw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DATABASE_URL)

# Create pgvector extension if it doesn't exist
with engine.connect() as connection:
    connection.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
    connection.commit()

Base = declarative_base()

class CodeComponent(Base):
    __tablename__ = 'code_components'
    
    id = Column(String, primary_key=True)
    title = Column(String)
    summary = Column(Text)
    code_snippet = Column(Text)
    code_embedding = Column(Vector(768))
    summary_embedding = Column(Vector(768))

# Initialize models after database setup
tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
model = AutoModel.from_pretrained('microsoft/codebert-base')
summary_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
summary_model = AutoModel.from_pretrained('bert-base-uncased')

# Create tables
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def generate_title_and_summary(code: str) -> Dict[str, str]:
    """Generate title and summary using GROQ."""
    try:
        # Generate title
        title_response = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Generate a short, descriptive title for this UI component. Keep it under 6 words."
                },
                {
                    "role": "user",
                    "content": f"Generate a title for this component:\n{code[:1000]}"
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=30,
        )
        
        # Generate summary
        summary_response = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Provide a brief, technical summary of this UI component. Focus on key features and functionality."
                },
                {
                    "role": "user",
                    "content": f"Summarize this component:\n{code[:2000]}"
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=150,
        )
        
        return {
            "title": title_response.choices[0].message.content.strip(),
            "summary": summary_response.choices[0].message.content.strip()
        }
    except Exception as e:
        print(f"Error generating title/summary: {e}")
        return {"title": "Untitled Component", "summary": "No summary available"}

def get_code_embedding(code: str) -> List[float]:
    """Generate CodeBERT embedding for code snippet."""
    try:
        inputs = tokenizer(code, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        # Use [CLS] token embedding
        return outputs.last_hidden_state[0][0].numpy().tolist()
    except Exception as e:
        print(f"Error generating code embedding: {e}")
        return np.zeros(768).tolist()

def get_summary_embedding(summary: str) -> List[float]:
    """Generate BERT embedding for summary text."""
    try:
        inputs = summary_tokenizer(summary, padding=True, truncation=True, max_length=512, return_tensors="pt")
        with torch.no_grad():
            outputs = summary_model(**inputs)
        return outputs.last_hidden_state[0][0].numpy().tolist()
    except Exception as e:
        print(f"Error generating summary embedding: {e}")
        return np.zeros(768).tolist()

def process_components():
    """Process components from JSON and store in database."""
    session = Session()
    
    try:
        json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraped-components', 'components.json')
        
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Components file not found at: {json_path}")
            
        print(f"Reading components from: {json_path}")
        
        with open(json_path, 'r') as f:
            components = json.load(f)
        
        # Start from component 67
        START_INDEX = 783
        total_components = len(components)
        
        print(f"Resuming from component {START_INDEX}/{total_components}")
        
        for idx, component in enumerate(components[START_INDEX:], start=START_INDEX):
            print(f"\nProcessing component {idx}/{total_components}")
            
            # Check if component already exists in database
            existing = session.query(CodeComponent).filter_by(id=f"component_{idx}").first()
            if existing:
                print(f"Skipping component {idx} - already processed")
                continue
            
            if not isinstance(component, dict):
                print(f"Skipping invalid component at index {idx}")
                continue
                
            html_code = component.get('htmlCode', '')
            if not html_code:
                print(f"Skipping component {idx} - no HTML code found")
                continue
                
            try:
                # Generate title and summary
                generated = generate_title_and_summary(html_code)
                title = generated['title']
                summary = generated['summary']
                
                print(f"Title: {title}")
                print("Generating embeddings...")
                
                # Generate embeddings
                code_embedding = get_code_embedding(html_code)
                summary_embedding = get_summary_embedding(summary)
                
                # Create database entry
                code_component = CodeComponent(
                    id=f"component_{idx}",
                    title=title,
                    summary=summary,
                    code_snippet=html_code,
                    code_embedding=code_embedding,
                    summary_embedding=summary_embedding
                )
                
                session.add(code_component)
                session.commit()
                print(f"Saved component {idx} to database")
                
            except Exception as e:
                print(f"Error processing component {idx}: {e}")
                session.rollback()
                continue
        
        print("\nAll remaining components processed successfully!")
        
    except Exception as e:
        print(f"Error processing components: {e}")
        session.rollback()
    finally:
        session.close()
        print("Database session closed")

if __name__ == "__main__":
    print("Starting component processing from index 67...")
    os.makedirs('scraped-components', exist_ok=True)
    process_components()