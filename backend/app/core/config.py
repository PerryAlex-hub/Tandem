from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    leetcode_api_base: str = "http://127.0.0.1:3001"
    piston_base: str = "http://127.0.0.1:2000"
    redis_url: str = "redis://127.0.0.1:6379/0"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()