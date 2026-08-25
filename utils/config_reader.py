import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _load_yaml() -> dict[str, Any]:
    config_path = PROJECT_ROOT / "config" / "config.yaml"
    with config_path.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file) or {}


_CONFIG = _load_yaml()


def get_environment_name() -> str:
    return os.getenv("ENVIRONMENT", "demo").strip().lower() or "demo"


def get_config(section: str, key: str, default: Any = None) -> Any:
    """Read an environment override, then YAML, then the supplied default."""
    environment_key = f"{section}_{key}".upper()
    environment_value = os.getenv(environment_key)
    if environment_value is not None:
        return environment_value
    return _CONFIG.get(section, {}).get(key, default)


def get_base_url() -> str:
    explicit_url = os.getenv("BASE_URL") or os.getenv("ORANGEHRM_URL")
    if explicit_url:
        return explicit_url

    environment_url = os.getenv(f"{get_environment_name().upper()}_BASE_URL")
    if environment_url:
        return environment_url

    environment_config = _CONFIG.get("environments", {}).get(get_environment_name(), {})
    configured_url = environment_config.get("base_url")
    if configured_url:
        return str(configured_url)

    application_url = _CONFIG.get("application", {}).get("base_url")
    if application_url:
        return str(application_url)
    raise RuntimeError(
        "Missing application URL. Set BASE_URL or <ENVIRONMENT>_BASE_URL."
    )


def get_timeout() -> int:
    return int(os.getenv("TIMEOUT", get_config("application", "timeout", 10_000)))


def get_browser_name() -> str:
    return str(os.getenv("BROWSER_NAME", get_config("browser", "name", "chromium")))
