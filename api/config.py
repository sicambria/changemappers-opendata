"""
API Configuration
"""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    app_name: str = "ChangeMappers OpenData API"
    app_version: str = "1.1.0"
    app_description: str = "REST API for accessing the ChangeMappers knowledge graph"
    
    data_dir: Path = Path(__file__).parent.parent / "data" / "entities"
    schemas_dir: Path = Path(__file__).parent.parent / "schemas" / "entities"
    
    rate_limit_requests: int = 100
    rate_limit_period_hours: int = 1
    
    cors_origins: list[str] = ["*"]
    
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
