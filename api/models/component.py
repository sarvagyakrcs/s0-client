"""
Models for component data structures and database interactions.
"""
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

class Component(BaseModel):
    """
    Represents a UI component in the database.
    """
    id: UUID
    title: str
    summary: str
    code_snippet: str
    code_embedding: List[float]
    summary_embedding: List[float]
    
    class Config:
        from_attributes = True

class ComponentMatch(BaseModel):
    """
    Represents a matched component with similarity score.
    """
    id: UUID
    title: str
    summary: str
    code_snippet: str
    similarity_score: float 