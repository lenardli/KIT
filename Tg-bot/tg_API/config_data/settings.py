import os

from dotenv import load_dotenv, find_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings


if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()


class SiteSettings(BaseSettings):
    TG_key: SecretStr = os.getenv("TG_KEY", None)
