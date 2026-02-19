from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Manus
    manus_api_key: str = Field(..., description="Manus API Key")
    manus_api_base_url: str = Field(
        default="https://api.manus.im/v1",
        description="Manus API Base URL",
    )
    manus_project_id: str = Field(default="", description="Manus Project ID")

    # LLM
    openai_api_key: str = Field(default="", description="OpenAI API Key")

    # Teams / Azure
    microsoft_app_id: str = Field(default="", description="Azure AD App ID")
    microsoft_app_password: str = Field(default="", description="Azure AD App Secret")
    microsoft_tenant_id: str = Field(default="", description="Azure AD Tenant ID (Single Tenant)")

    # Datenbank
    database_url: str = Field(
        default="sqlite:///./salesbot.db",
        description="Database connection string",
    )

    # Allgemein
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")
    require_confirmation: bool = Field(
        default=True,
        description="Bot zeigt Zusammenfassung und wartet auf Bestätigung",
    )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
