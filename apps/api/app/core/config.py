from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "SignOff AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    DATABASE_URL: str = "mysql+asyncmy://signoff_user:signoff_password@localhost:3306/signoff"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str = "super-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    SUPABASE_URL: str = "https://YOUR-PROJECT-ID.supabase.co"
    SUPABASE_SERVICE_ROLE_KEY: str = "your-super-secret-service-role-key"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:3b"
    
    STRIPE_SECRET_KEY: str = "sk_test_your_stripe_secret_key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_your_stripe_webhook_secret"

    model_config = {"env_file": ".env", "case_sensitive": True, "env_nested_delimiter": "__"}

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()