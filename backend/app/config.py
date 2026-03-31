from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "GEOFABRIC_"}

    database_url: str = (
        "postgresql+asyncpg://geofabric:geofabric@localhost:5432/geofabric"
    )
    upload_dir: str = "./uploads"
    max_upload_bytes: int = 100 * 1024 * 1024  # 100 MB
    allowed_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
