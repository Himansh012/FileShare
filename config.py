from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
DATABASE = BASE_DIR / "fileshare.db"

MAX_CONTENT_LENGTH = 1024 * 1024 * 1024
MAX_FILE_PER_UPLOAD = 10
