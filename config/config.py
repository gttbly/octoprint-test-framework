import os
from dotenv import load_dotenv

# 获取项目根目录，确保在任何地方都能找到 .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    BASE_URL = os.getenv("OCTOPRINT_URL", "http://localhost:5000")
    API_KEY = os.getenv("OCTOPRINT_API_KEY", "")
    USERNAME = os.getenv("OCTOPRINT_USERNAME", "")
    PASSWORD = os.getenv("OCTOPRINT_PASSWORD", "")
    HEADLESS = True
    TIMEOUT = 10
