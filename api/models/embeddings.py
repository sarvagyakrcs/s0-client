"""
Models for handling embeddings and vector operations.
"""
from typing import List
import torch
from transformers import AutoTokenizer, AutoModel

class EmbeddingModel:
    """
    Handles the generation and management of embeddings using transformer models.
    """
    def __init__(self, model_name: str):
        """
        Initialize the embedding model with specified transformer.
        
        Args:
            model_name (str): Name of the HuggingFace model to use
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embeddings for given text.
        
        Args:
            text (str): Input text to generate embeddings for
            
        Returns:
            List[float]: Vector representation of the text
        """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().tolist() 