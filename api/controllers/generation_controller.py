"""
Controllers for handling component generation and search requests.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from api.services.ai_service import AIService
from api.models.component import ComponentMatch
from api.database import get_db
from api.config import get_settings, Settings

router = APIRouter()

class GenerationRequest(BaseModel):
    """Request model for component generation."""
    query: str
    output_format: str
    similar_count: int = 3

class GenerationResponse(BaseModel):
    """Response model for component generation."""
    generated_code: str
    similar_components: List[ComponentMatch]
    explanation: str

@router.post("/generate", response_model=GenerationResponse)
async def generate_component(
    request: GenerationRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Generate a component based on user query.
    
    Args:
        request (GenerationRequest): Generation parameters
        
    Returns:
        GenerationResponse: Generated component and similar matches
        
    Raises:
        HTTPException: If generation fails
    """
    try:
        ai_service = AIService(settings)
        db = get_db()
        
        # Find similar components
        components = db.get_all_components()
        similar = ai_service.find_similar_components(
            request.query,
            components,
            request.similar_count
        )
        
        # Generate new component
        code, explanation = await ai_service.generate_component(
            request.query,
            similar,
            request.output_format
        )
        
        return GenerationResponse(
            generated_code=code,
            similar_components=similar,
            explanation=explanation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 