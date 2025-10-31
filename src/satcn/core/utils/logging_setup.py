import logging
import json
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON.
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "log_level": record.levelname,
            "message": record.getMessage()
        }
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
        return json.dumps(log_record)

def setup_logging():
    """
    Sets up a JSON logger.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)

    return logger
