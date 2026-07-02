# utils/logger.py
import logging
import sys
from config.constants import LOG_LEVEL, LOG_FILE
from pathlib import Path

def setup_logger(name: str = "vpd") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, "INFO", logging.INFO))

    if not logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(LOG_FILE)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        except Exception:
            pass

    return logger

logger = setup_logger()