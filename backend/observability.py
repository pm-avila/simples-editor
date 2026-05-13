import json
import sys
from datetime import datetime, timezone


def log_event(logger: str, event: str, level: str = "INFO", **fields) -> None:
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "level": level,
        "logger": logger,
        "event": event,
    }
    for key, value in fields.items():
        if value is not None:
            payload[key] = value
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()
