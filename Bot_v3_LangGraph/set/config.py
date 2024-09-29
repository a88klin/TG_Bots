from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=r'set/.env',
                                      env_file_encoding='utf-8')
    OPENAI_API_KEY: SecretStr
    TAVILY_API_KEY: SecretStr
    LANGCHAIN_API_KEY: SecretStr
    BOT_TOKEN: SecretStr
    OPEN_WEATHER_TOKEN: SecretStr

    GOOGLE_SERVICE_STT: str
    GOOGLE_SERVICE_TAB: str
    GOOGLE_SERVICE_CALENDAR: str
    GOOGLE_CALENDAR_TOKEN: str
    LINK_NOTEPAD: str

    ALLOWED_IDS: list


config = Settings()
