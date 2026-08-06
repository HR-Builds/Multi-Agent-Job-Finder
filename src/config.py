from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Project configuration.
    """

    # Gemini
    GOOGLE_API_KEY: str
    MODEL_NAME: str = "gemini-2.5-flash"
    TEMPERATURE: float = 0.2

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"

    SAMPLE_RESUME_DIR: Path = DATA_DIR / "sample_resumes"

    SUPPORTED_EXTENSIONS: tuple[str, ...] = (
        ".pdf",
        ".docx",
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()