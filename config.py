import os
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

class Config:
    """Base application configuration class."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-secret-key-12345")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin_secret_pass")

    # Absolute directory paths
    BASE_DIR = BASE_DIR
    DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, os.getenv("DATABASE_PATH", "ota_database.db")))
    FIRMWARE_DIR = os.path.abspath(os.path.join(BASE_DIR, os.getenv("FIRMWARE_DIR", "firmware")))
    LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, os.getenv("LOG_DIR", "logs")))
    LOG_FILE = os.path.join(LOG_DIR, "ota_system.log")

    # Upload restrictions
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {"bin"}
