from pathlib import Path
from datetime import datetime
import json


BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "data" / "logs"
LOG_FILE = LOG_DIR / "pipeline_log.jsonl"


def log_event(event_type: str, message: str, serial_number: str | None = None, source_type: str | None = None, extra: dict | None = None):
    """
    Write one structured log event as a JSON line.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event_type": event_type,
        "message": message,
        "serial_number": serial_number,
        "source_type": source_type,
        "extra": extra or {}
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def reset_log():
    """
    Optional helper to clear the log file.
    """
    if LOG_FILE.exists():
        LOG_FILE.unlink()


def get_log_path() -> str:
    return str(LOG_FILE)