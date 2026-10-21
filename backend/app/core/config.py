
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"


settings = Settings()
