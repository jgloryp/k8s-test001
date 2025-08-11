from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application settings
    app_name: str = "sample2-app"
    app_version: str = "1.0.0"
    description: str = "DevOps 파이프라인 데모용 Python FastAPI 샘플 애플리케이션"
    
    # Server settings
    port: int = 3000
    host: str = "0.0.0.0"
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Security
    show_docs_environment: List[str] = ["development", "staging"]
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # External service URLs
    sample_app_url: str = "http://sample-app:3000"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()