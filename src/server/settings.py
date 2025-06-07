from pathlib import Path
from starlette.config import Config
from starlette.datastructures import Secret

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=True)

EMAIL_ADDRESS = config("EMAIL_ADDRESS", default="")

POSTGRES_USERNAME = config("POSTGRES_USERNAME")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_URL = config("POSTGRES_URL")
POSTGRES_VOLUME_PATH = config("POSTGRES_VOLUME_PATH")
