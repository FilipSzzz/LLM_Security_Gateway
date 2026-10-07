from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: SecretStr
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    default_model: str = "nvidia/nemotron-3-super-120b-a12b:free"

    upstream_connect_timeout: float = 5.0
    upstream_read_timeout: float = 60.0

    log_level: str = "INFO"
    log_json: bool = False


settings = Settings()
