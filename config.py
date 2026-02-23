"""Configuration settings for the REST API library."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    database_url: str = "sqlite:///./app.db"
    
    # Alternative database URLs (uncomment to use):
    # PostgreSQL: "postgresql://user:password@localhost/dbname"
    # MySQL: "mysql://user:password@localhost/dbname"
    
    # API settings
    api_title: str = "REST API Library"
    api_version: str = "1.0.0"
    api_description: str = "A REST API library with database functionality"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
