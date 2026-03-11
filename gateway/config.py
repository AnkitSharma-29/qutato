from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "Qutato Gateway"
    DEBUG: bool = True
    
    # Security
    ADMIN_API_KEY: str = "qutato_admin_secret_key"
    
    # Redis Config
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # LLM Settings
    DEFAULT_THRESHOLD: float = 0.85
    
    class Config:
        env_file = ".env"

settings = Settings()
