import sys
import os
from loguru import logger


def configure_logging(settings):
    level = settings.LOG_LEVEL if hasattr(settings, "LOG_LEVEL") else os.getenv("LOG_LEVEL", "INFO")
    logger.remove()
    logger.add(sys.stdout, level=level, serialize=False)

