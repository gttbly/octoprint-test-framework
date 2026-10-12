import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def _as_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


class Config:
    BASE_URL = os.getenv("OCTOPRINT_URL", "http://localhost:5000").rstrip("/")
    API_KEY = os.getenv("OCTOPRINT_API_KEY", "")
    USERNAME = os.getenv("OCTOPRINT_USERNAME", "")
    PASSWORD = os.getenv("OCTOPRINT_PASSWORD", "")

    HEADLESS = _as_bool("HEADLESS", True)
    BROWSER = os.getenv("BROWSER", "chrome")
    DRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "")
    TIMEOUT = _as_int("UI_TIMEOUT", 15)
    LONG_TIMEOUT = _as_int("LONG_TIMEOUT", 60)
    API_TIMEOUT = _as_int("API_TIMEOUT", 15)

    ARTIFACT_DIR = Path(os.getenv("ARTIFACT_DIR", str(BASE_DIR / "artifacts")))
    SCREENSHOT_DIR = ARTIFACT_DIR / "screenshots"
    PAGE_SOURCE_DIR = ARTIFACT_DIR / "page-source"
