from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=5080, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")

    # EspoCRM Configuration
    espocrm_url: str = Field(..., description="EspoCRM instance URL")
    espocrm_api_key: str = Field(..., description="EspoCRM API key")

    # Gemini/OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key (Gemini)")
    openai_base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/",
        description="OpenAI base URL for Gemini",
    )
    openai_model: str = Field(
        default="gemini-1.5-flash", description="Model to use for skills extraction"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # Security
    webhook_secret: str = Field(..., description="Webhook secret for validation")

    # File Processing
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    allowed_file_types: str = Field(
        default="pdf,doc,docx", description="Allowed file types (comma-separated)"
    )

    # Cache Configuration
    enable_cache: bool = Field(default=True, description="Enable content caching")
    cache_ttl_hours: int = Field(default=24, description="Cache TTL in hours")

    @property
    def allowed_file_extensions(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_file_types.split(",")}


settings = Settings()
