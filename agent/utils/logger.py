import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Create a logger that prints timestamped messages to stdout.
    Usage: logger = get_logger(__name__)
           logger.info("Message received")
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Only add handler once (avoid duplicate logs on reload)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        ))
        logger.addHandler(handler)

    return logger
