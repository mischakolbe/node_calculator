"""
Module for logging

"""

import logging
import logging.handlers

log = logging.getLogger(__name__)

# Make sure logs don't propagate through to __main__ logger, too
# This might be a Maya-issue. I don't think this should be necessary!
log.propagate = False

# format_str = "%(asctime)s; %(levelname)s; %(message)s"
format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(format_str, "%m/%d/%Y %H:%M:%S")


class NullHandler(logging.Handler):

    def emit(self, record):
        pass


def clear_handlers():
    log.handlers = []
    nh = NullHandler()
    log.addHandler(nh)


def setup_stream_handler(level=logging.INFO):
    """
    Creates a stream handler for logging.

    Default level is info.
    Options: DEBUG, INFO, WARN, ERROR, CRITICAL
    """
    strmh = logging.StreamHandler()
    strmh.setFormatter(formatter)
    strmh.setLevel(level)
    log.addHandler(strmh)

    if log.getEffectiveLevel() > level:
        log.setLevel(level)


def setup_file_handler(file_path, max_bytes=100 << 20, level=logging.INFO):
    """
    Creates a rotating file handler for logging.

    Default level is info.

    max_bytes:
    x << y Returns x with the bits shifted to the left by y places. 100 << 20 === 100 * 2 ** 20
    """
    fh = logging.handlers.RotatingFileHandler(file_path, max_bytes=max_bytes, backupCount=10)
    fh.setFormatter(formatter)
    fh.setLevel(level)
    log.addHandler(fh)

    if log.getEffectiveLevel() > level:
        log.setLevel(level)

    log.info("Log file: {0}".format(file_path))
