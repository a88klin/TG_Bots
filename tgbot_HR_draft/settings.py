# pip install pydantic pydantic-settings
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8')
    bot_token: SecretStr
    openai_api_key: SecretStr
    admin_ids: list

    mongodb_host: str
    password: SecretStr
    user: str
    database: str

    vacancies_json_files: str
    resumes_json_files: str
    db_index_files: str
    pdf_report_files: str


settings = Settings()
