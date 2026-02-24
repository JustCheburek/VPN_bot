from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    BOT_TOKEN: str
    CHANNEL_ID: int
    ADMIN_ID: int

    XUI_HOST: str
    XUI_USERNAME: str
    XUI_PASSWORD: str
    XUI_INBOUND_IDS: list[int]


settings = Settings()
