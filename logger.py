"""
Logging module for node calculator
"""

import logging


# Get the logger of __name__ (most likely; __main__)
logger = logging.getLogger(__name__)
# Create an I/O stream handler
io_handler = logging.StreamHandler()
# Create a logging formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    '%m/%d/%Y %H:%M:%S',
)
# Assign the formatter to the io_handler
io_handler.setFormatter(formatter)
# Add the io_handler to the logger
logger.addHandler(io_handler)
# Only change the logging-level if it's above what we want it to be
noca_logging_level = logging.WARN  # Options: DEBUG, INFO, WARN, ERROR, CRITICAL
if logger.getEffectiveLevel() > noca_logging_level:
    logger.setLevel(noca_logging_level)
# Set the handler logging level
io_handler.setLevel(noca_logging_level)
