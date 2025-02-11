"""
Application configuration management.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    database_url: str = "postgresql://neondb_owner:npg_Xd63PzRbHcrn@ep-morning-shadow-a17ijyhw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    gemini_api_key: str = "AIzaSyAg7T6fOhjglzNWDPEP0nBDKBvY_kwwfzo"
    model_temperature: float = 0.7
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application configuration
    """
    return Settings() 