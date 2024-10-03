# pip install pydantic pydantic-settings
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='set/.env',
                                      env_file_encoding='utf-8')
    OPENAI_API_KEY: SecretStr
    TAVILY_API_KEY: SecretStr
    LANGCHAIN_API_KEY: SecretStr
    BOT_TOKEN: SecretStr

    BASE_URL: str

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


config = Settings()
