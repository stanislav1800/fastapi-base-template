import os
import logging.config
from pathlib import Path

from src.core.config import settings


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = os.path.join(LOG_DIR, "app.log")

LOG_LEVEL = settings.LOG_LEVEL.upper()

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            'format': '%(asctime)s | %(levelname)7s | %(name)s: %(message)s'
        },
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": (
                "%(asctime)s %(levelname)s %(name)s "
                "%(message)s %(filename)s "
                "%(funcName)s %(lineno)d"
            ),
            "datefmt": "%d-%m-%Y %H:%M:%S"
        },
    },
    "handlers": {
        'stream_standard_handler': {
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'stream_json_handler': {
            'formatter': 'json',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file_handler': {
            'formatter': 'json',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': log_file,
            'maxBytes': 1024 * 1024 * 1,  # = 1MB
            'backupCount': 3,
        },
    },
    "loggers": {
        "root": {
            "level": LOG_LEVEL,
            "handlers": ["stream_standard_handler", "file_handler"],
            # 'filters': ['message_filter'],
            "propagate": False,
        },
        'uvicorn': {
            'handlers': ['stream_standard_handler', 'file_handler'],
            # 'filters': ['message_filter'],
            'level': LOG_LEVEL,
            'propagate': False
        },
        'uvicorn.access': {
            'handlers': ['stream_standard_handler', 'file_handler'],
            # 'filters': ['message_filter'],
            'level': LOG_LEVEL,
            'propagate': False
        },
        'uvicorn.error': {
            'handlers': ['stream_standard_handler', 'file_handler'],
            # 'filters': ['message_filter'],
            'level': LOG_LEVEL,
            'propagate': False
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
