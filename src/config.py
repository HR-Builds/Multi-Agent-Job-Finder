from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Explicitly load .env from the project root before validating settings
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings(BaseSettings):
    # Gemini Configuration
    GROQ_API_KEY: str
    MODEL_NAME: str = "openai/gpt-oss-120b"
    TEMPERATURE: float = 0.7
    MAX_SEARCH_RESULTS: int = 5

    # Search Configuration
    TAVILY_API_KEY: str

    # Paths (Dynamically derived using BASE_DIR)
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    SAMPLE_RESUME_DIR: Path = BASE_DIR / "data" / "sample_resumes"

    # Resume Formats
    SUPPORTED_EXTENSIONS: tuple[str, ...] = (".pdf", ".docx")

    # Modern Pydantic V2 Configuration
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        extra="ignore",
        env_file_encoding="utf-8"
    )

settings = Settings()