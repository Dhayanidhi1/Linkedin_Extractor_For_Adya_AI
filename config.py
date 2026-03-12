import os
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
KEYWORDS = [k.strip() for k in os.getenv("KEYWORDS", "Shayak Mazumder,Adya AI").split(",")]
MONTHS_BACK = int(os.getenv("MONTHS_BACK", "6"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
USE_PROXY = os.getenv("USE_PROXY", "false").lower() == "true"
PROXY_SERVER = os.getenv("PROXY_SERVER", "")
PROXY_USERNAME = os.getenv("PROXY_USERNAME", "")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "")

os.makedirs(OUTPUT_DIR, exist_ok=True)
