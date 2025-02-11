"""
Service layer for AI operations including component generation and similarity search.
"""
from typing import List, Tuple
import google.generativeai as genai
from api.models.component import Component, ComponentMatch
from api.models.embeddings import EmbeddingModel
from api.config import Settings

class AIService:
    """
    Handles AI operations including generation and similarity matching.
    """
    def __init__(self, settings: Settings):
        """
        Initialize AI service with necessary models and configurations.
        
        Args:
            settings (Settings): Application configuration
        """
        self.code_embedder = EmbeddingModel("microsoft/codebert-base")
        self.text_embedder = EmbeddingModel("bert-base-uncoded")
        self.gemini = genai.GenerativeModel('gemini-pro')
        self._configure_gemini(settings)
        
    def _configure_gemini(self, settings: Settings):
        """Configure Gemini AI with API key and settings."""
        genai.configure(api_key=settings.gemini_api_key)
        self.generation_config = {
            "temperature": settings.model_temperature,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
    def _compute_similarities(self, query_embedding: List[float], components: List[Component]) -> List[ComponentMatch]:
        """Compute similarity scores between query and components."""
        # Placeholder implementation
        return []
        
    def _build_generation_prompt(self, query: str, similar_components: List[ComponentMatch], output_format: str) -> str:
        """Build prompt for component generation."""
        return f"Generate a {output_format} component for: {query}"
        
    def _parse_generation_response(self, response) -> Tuple[str, str]:
        """Parse Gemini AI response into code and explanation."""
        # Placeholder implementation
        return response.text, "Generated based on your requirements"
    
    def find_similar_components(
        self, 
        query: str, 
        components: List[Component], 
        limit: int = 3
    ) -> List[ComponentMatch]:
        """
        Find similar components based on query embeddings.
        
        Args:
            query (str): Search query
            components (List[Component]): Available components
            limit (int): Maximum number of matches to return
            
        Returns:
            List[ComponentMatch]: Sorted list of similar components
        """
        query_embedding = self.text_embedder.generate_embedding(query)
        matches = self._compute_similarities(query_embedding, components)
        return matches[:limit]
    
    async def generate_component(
        self,
        query: str,
        similar_components: List[ComponentMatch],
        output_format: str
    ) -> Tuple[str, str]:
        """
        Generate a new component based on query and similar components.
        
        Args:
            query (str): User's component request
            similar_components (List[ComponentMatch]): Similar existing components
            output_format (str): Desired output format (html/jsx-js/jsx-ts)
            
        Returns:
            Tuple[str, str]: Generated code and explanation
        """
        prompt = self._build_generation_prompt(query, similar_components, output_format)
        response = await self.gemini.generate_content(prompt)
        return self._parse_generation_response(response) 