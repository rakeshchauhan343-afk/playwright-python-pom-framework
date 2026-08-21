import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _required_setting(name: str) -> str:
	value = os.getenv(name)
	if not value:
		raise RuntimeError(f"Missing required setting: {name}. Add it to .env.")
	return value


ORANGEHRM_URL = _required_setting("ORANGEHRM_URL")
ORANGEHRM_USERNAME = _required_setting("ORANGEHRM_USERNAME")
ORANGEHRM_PASSWORD = _required_setting("ORANGEHRM_PASSWORD")
