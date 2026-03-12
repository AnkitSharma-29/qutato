from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # Qutato Core Config
    APP_NAME: str = "Qutato Smart Core"
    DEBUG: bool = False
    
    # Security
    # In production, ALWAYS set this via ADMIN_API_KEY environment variable.
    ADMIN_API_KEY: str = "qutato_admin_secret_key"
    
    # Redis Config
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # LLM Settings
    DEFAULT_THRESHOLD: float = 0.85

    # Logging
    LOG_FILE: str = "qutato.log"

    # Universal Gateway — which API formats to enable
    ENABLED_FORMATS: List[str] = ["openai", "anthropic", "gemini", "ollama"]
    
    class Config:
        env_file = ".env"

settings = Settings()
