import logging
import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Also print to console
    ]
)

logger = logging.getLogger("korba_api")


def _truncate(value: Optional[str], max_chars: int = 300) -> str:
    """Keep log lines compact while still preserving useful context."""
    if value is None:
        return ""
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}...<truncated>"


def log_api_response(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    query_string: str = "",
) -> None:
    """Log every API response with SUCCESS/FAILURE classification."""
    outcome = "SUCCESS" if 200 <= status_code < 400 else "FAILURE"
    base_message = (
        "API_RESPONSE | outcome=%s | method=%s | path=%s | status=%s | "
        "duration_ms=%.2f"
    )

    if query_string:
        base_message += " | query=%s"
        args = (
            outcome,
            method,
            path,
            status_code,
            duration_ms,
            _truncate(query_string),
        )
    else:
        args = (outcome, method, path, status_code, duration_ms)

    if outcome == "SUCCESS":
        logger.info(base_message, *args)
    else:
        logger.warning(base_message, *args)