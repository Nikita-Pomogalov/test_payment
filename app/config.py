from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "payment_user"
    DB_PASSWORD: str = "payment_pass"
    DB_NAME: str = "payment_db"
    DB_ECHO: bool = False

    # Security
    SECRET_KEY: str = "gfdmhghif38yrf9ew0jkf32"
    JWT_SECRET: str = "your_jwt_secret_key_here_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXP: int = 3600
    JWT_REFRESH_EXP: int = 86400

    # Default admin
    ADMIN_EMAIL: str = "admin@test.com"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_FULL_NAME: str = "Admin User"

    # Default user
    USER_EMAIL: str = "user@test.com"
    USER_PASSWORD: str = "user123"
    USER_FULL_NAME: str = "Test User"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()