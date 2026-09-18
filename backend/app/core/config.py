from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PackagePro"
    
    # Database
    DATABASE_URL: str = "postgresql://packagepro_user:packagepro_password@localhost/packagepro"
    
    # Redis (for Celery and SSE)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
