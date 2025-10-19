import logging

default_format: str = "{asctime} [{levelname}] {module} | {message}"
default_date_format: str = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=default_format, datefmt=default_date_format, style="{")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
