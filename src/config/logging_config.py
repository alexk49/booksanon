import os
import logging
import logging.config
import contextvars

from .settings import PROJECT_ROOT, DEBUG

if DEBUG:
    logging_level = "DEBUG"
else:
    logging_level = "INFO"

# Context variable for per-request ID
request_id_var = contextvars.ContextVar("request_id", default="-")

LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)


class RequestIDLogFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - [%(request_id)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },

    "filters": {
        "request_id": {
            "()": RequestIDLogFilter,
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["request_id"],
        },
        "app_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, "app.log"),
            "formatter": "default",
            "filters": ["request_id"],
            "maxBytes": 1_000_000,
            "backupCount": 3,
        },
        "tasks_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, "tasks.log"),
            "formatter": "default",
            "filters": ["request_id"],
            "maxBytes": 1_000_000,
            "backupCount": 3,
        },
        "calls_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_DIR, "calls.log"),
            "formatter": "default",
            "filters": ["request_id"],
            "maxBytes": 1_000_000,
            "backupCount": 3,
        },
    },

    "root": {
        "level": logging_level,
        "handlers": ["console", "app_file"],
    },

    "loggers": {
        "app": {
            "level": logging_level,
            "handlers": ["console", "app_file"],
            "propagate": False,
        },
        "app.tasks": {
            "level": logging_level,
            "handlers": ["console", "tasks_file"],
            "propagate": False,
        },
        "app.calls": {
            "level": logging_level,
            "handlers": ["console", "calls_file"],
            "propagate": False,
        },
    }
}
