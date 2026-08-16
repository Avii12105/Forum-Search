from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ForumSearch API"
    API_V1_STR: str = "/api"
    FRONTEND_CORS_ORIGIN: str = "http://localhost:5173"
    
    # Database Settings
    DATABASE_URL: str
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()