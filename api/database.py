"""
Database connection and operations.
"""
from sqlalchemy import create_engine
from functools import lru_cache

@lru_cache()
def get_db():
    """Get database connection."""
    DATABASE_URL = "postgresql://neondb_owner:npg_Xd63PzRbHcrn@ep-morning-shadow-a17ijyhw-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    engine = create_engine(DATABASE_URL)
    return engine 