from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # File storage
    UPLOAD_DIR: str = "./uploads"
    PROCESSED_DIR: str = "./processed"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png"}

    # Static files
    STATIC_FILES_DIR: str = "./static"

    # Models
    CLASSIFIER_MODEL_PATH: str = "./models/classifier.keras"
    DENOISER_MODEL_PATH: str = "./models/denoiser.keras"
    CAPTIONER_MODEL_PATH: str = "./models/captioner.keras"

    # Processing
    MAX_CONCURRENT_PROCESSES: int = 3

    class Config:
        env_file = ".env"


settings = Settings()
