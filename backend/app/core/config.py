from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    leetcode_api_base: str = "http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()