"""Config dict for log files"""
from os.path import exists, join
from os import mkdir

LOGS_DIR = "logs"
LOGS_FILE = "booksanon-logs.txt"
LOGS_FILE_PATH = join(LOGS_DIR, LOGS_FILE)

if exists(LOGS_DIR) is False:
    mkdir(LOGS_DIR)

if not (LOGS_FILE_PATH):
    open(LOGS_FILE_PATH, "w").close()  # create empty log file

# configire logs
config_dict = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%B %d, %Y %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_FILE_PATH,
            "formatter": "default",
            "mode": "a",
            "maxBytes": 100000,
            "backupCount": 2,
        },
    },
    "root": {"level": "DEBUG", "handlers": ["console", "file"]},
}
