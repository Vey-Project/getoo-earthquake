"""
utils/logger.py - Setup logging
"""
import logging
import os
import sys
from datetime import datetime

from config import LOG_LEVEL


def setup_logger():
    """Setup logging ke console dan file"""
    os.makedirs("logs", exist_ok=True)

    log_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)

    # File handler
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = logging.FileHandler(f"logs/bot-{today}.log", encoding="utf-8")
    file_handler.setFormatter(log_format)

    root = logging.getLogger()
    root.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)