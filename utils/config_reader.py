import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from config.settings import ORANGEHRM_URL

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _load_yaml() -> dict[str, Any]:
    config_path = PROJECT_ROOT / "config" / "config.yaml"
    with config_path.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file) or {}


_CONFIG = _load_yaml()


def get_config(section: str, key: str, default: Any = None) -> Any:
    """Read an environment override, then YAML, then the supplied default."""
    environment_key = f"{section}_{key}".upper()
    environment_value = os.getenv(environment_key)
    if environment_value is not None:
        return environment_value
    return _CONFIG.get(section, {}).get(key, default)


def get_base_url() -> str:
    return ORANGEHRM_URL


def get_timeout() -> int:
    return int(os.getenv("TIMEOUT", get_config("application", "timeout", 10_000)))
