from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str = "sqlite:///./weatherbot.db"

    class Config:
        env_file = ".env"


settings = Settings()