from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8')
    BOT_TOKEN: SecretStr
    OPENAI_API_KEY: SecretStr
    ADMIN_IDS: list

    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int

    @property
    def DATABASE_URL_asyncpg(self):
        # postgresql+asyncpg://user:password@host:port/db_name
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@" \
               f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
