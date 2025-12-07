from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./dev.db"
    storage_path: Path = Path("storage")

    class Config:
        env_prefix = "PARTSUITE_"
        env_file = ".env"


def get_settings() -> Settings:
    settings = Settings()
    settings.storage_path.mkdir(parents=True, exist_ok=True)
    (settings.storage_path / "originals").mkdir(parents=True, exist_ok=True)
    (settings.storage_path / "summaries").mkdir(parents=True, exist_ok=True)
    return settings
