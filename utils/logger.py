import logging
from pathlib import Path


def get_logger(name: str = "playwright_pom") -> logging.Logger:
    """Return a logger configured for console and report-file output."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    report_dir = Path(__file__).resolve().parents[1] / "reports"
    report_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(report_dir / "framework.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
