import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application settings
    app_name: str = "Text-to-SQL Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql://username:password@db.supabase.co:5432/postgres"
    
    # Supabase specific settings (optional, for future features)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    # LLM settings
    llm_model_name: str = "microsoft/DialoGPT-medium"  # Default model
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"  # Updated to supported production model
    max_tokens: int = 512
    temperature: float = 0.7
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Security settings
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
