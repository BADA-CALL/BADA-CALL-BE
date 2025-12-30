from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()