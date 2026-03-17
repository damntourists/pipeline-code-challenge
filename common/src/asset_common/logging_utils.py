import logging

from flask import request, has_request_context

class RequestIdFilter(logging.Filter):
    """
    Custom logging filter to add request ID to log records.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if has_request_context():
            record.request_id = request.headers.get("X-Request-Id", "system", type=str)
        else:
            record.request_id = str("system")
        return True


def setup_logger(name: str) -> logging.Logger:
    """
    Sets up a logger with a custom formatter that includes request ID.
    """
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(request_id)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())
    logger.addHandler(handler)
    return logger
