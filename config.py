import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Secret Key
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-key-12345"

    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Database configuration - ✅ INSTANCE FOLDER मध्ये
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.sqlite3')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    # Gemini API
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

    # ML Model Paths - ✅ .h5 extension add केलं
    MODEL_PATH = os.path.join("ml_model", "crop_disease_model.h5")
    CLASS_INDICES_PATH = os.path.join("ml_model", "class_indices.json")