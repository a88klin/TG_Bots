# pip install pydantic pydantic-settings
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='input',
                                      env_file_encoding='utf-8')
    bot_token: SecretStr
    admin_id: int
    allowed_ids: list

    gpt_secret_key: SecretStr

    host: str
    password: SecretStr
    user: str
    database: str


config = Settings()
