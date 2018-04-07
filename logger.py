"""Module for logging

:created: 03/04/2018
:author: Mischa Kolbe <mik@dneg.com>
:credits: Steven Bills, Mischa Kolbe

"""


import logging
import logging.handlers

log = logging.getLogger(__name__)

# Make sure logs don't propagate through to __main__ logger, too
# This might be a Maya-issue. I don't think this should be necessary!
log.propagate = False

FORMAT_STR = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FORMATTER = logging.Formatter(FORMAT_STR, "%m/%d/%Y %H:%M:%S")


class NullHandler(logging.Handler):
    """ Basic custom handler """

    def emit(self, record):
        pass


def clear_handlers():
    """
    Reset handlers of logger.
    This prevents creating multiple handler copies when using reload(logger).
    """
    log.handlers = []
    null_handler = NullHandler()
    log.addHandler(null_handler)


def setup_stream_handler(level=logging.INFO):
    """
    Creates a stream handler for logging.

    Default level is info.
    Options: DEBUG, INFO, WARN, ERROR, CRITICAL
    """
    strmh = logging.StreamHandler()
    strmh.setFormatter(FORMATTER)
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
    file_handler = logging.handlers.RotatingFileHandler(
        file_path,
        maxBytes=max_bytes,
        backupCount=10
    )
    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel(level)
    log.addHandler(file_handler)

    if log.getEffectiveLevel() > level:
        log.setLevel(level)

    log.info("Log file: {0}".format(file_path))
