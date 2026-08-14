from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Класс настроек приложения с автоматической валидацией и чтением из файла .env"""
    BOT_TOKEN: str
    DB_URL: str
    REDIS_URL: str

    # Конфигурация Pydantic для чтения .env в кодировке UTF-8
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Создаем синглтон настроек для импорта в других модулях
settings = Settings()