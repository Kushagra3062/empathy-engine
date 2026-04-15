from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
import os

class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMP_AUDIO_DIR: Path = BASE_DIR.parent / "temp_audio"
    
    PROJECT_NAME: str = "The Empathy Engine"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Models
    DISTILBERT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    ROBERTA_MODEL: str = "cardiffnlp/twitter-roberta-base-emotion"
    DEVICE: str = "cpu"
    
    # Audio & TTS
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = "./credentials.json"
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: Optional[str] = f"sqlite:///../../empathy_engine_v2.db"
    REDIS_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True,
        extra="ignore" 
    )

settings = Settings()
