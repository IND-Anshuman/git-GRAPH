from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = "local"
    debug: bool = False
    database_url: str = "postgresql://postgres:postgres@localhost:5432/git_graph_dev"
    storage_root: str = "./data/repositories"
    allowed_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
