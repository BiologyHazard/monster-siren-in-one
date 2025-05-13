import logging

default_format: str = '{asctime} [{levelname}] {module} | {message}'
default_date_format: str = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(level=logging.INFO, format=default_format, datefmt=default_date_format, style='{')

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
