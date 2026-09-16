from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Facebook Messenger
    facebook_page_access_token: str = ""
    facebook_verify_token: str = "my_verify_token_123"
    facebook_app_secret: str = ""

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4"

    # Google Sheets
    google_sheets_credentials_file: str = "credentials.json"
    google_sheets_url: str = ""

    # Business Configuration
    business_name: str = "Our Store"
    business_hours_start: str = "09:00"
    business_hours_end: str = "18:00"
    business_timezone: str = "UTC"
    business_phone: str = ""
    business_email: str = ""

    # Scheduling
    calendar_api_key: str = ""
    calendar_id: str = "primary"

    # Human Handoff
    human_handoff_keywords: list[str] = ["human", "agent", "support", "help"]

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def get_settings() -> Settings:
    return settings