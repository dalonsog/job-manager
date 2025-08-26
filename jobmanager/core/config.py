from pydantic_settings import BaseSettings, SettingsConfigDict

VERSION = "0.1.0"


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    ADMIN_ACCOUNT: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str = sqlite_url


settings = Settings()
