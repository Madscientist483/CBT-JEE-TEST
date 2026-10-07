from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    cors_origins: str = "*"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
