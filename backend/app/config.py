from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MySQL
    mysql_host: str = "mysql"
    mysql_port: int = 3306
    mysql_user: str = "keygen"
    mysql_password: str = "change_me_in_production"
    mysql_database: str = "keygen"

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # JWT
    jwt_secret_key: str = "change_me_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    # Admin
    admin_default_username: str = "admin"
    admin_default_password: str = "admin123"

    # App
    app_env: str = "development"
    app_debug: bool = True

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
