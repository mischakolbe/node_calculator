"""
Logging module for node calculator
"""

import logging

noca_logging_level = logging.WARN  # Options: DEBUG, INFO, WARN, ERROR, CRITICAL

# Get the logger of __name__
logger = logging.getLogger(__name__)
# Make sure logs don't propagate through to __main__ logger, too
logger.propagate = False

# Make sure only one handler is present, otherwise duplicate streams can occur
if not len(logger.handlers):
    # Create a logging formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        '%m/%d/%Y %H:%M:%S',
    )

    # Create an I/O stream handler
    stream_handler = logging.StreamHandler()
    # Assign the formatter to the stream_handler
    stream_handler.setFormatter(formatter)
    # Set the handler logging level
    stream_handler.setLevel(noca_logging_level)
    # Add the stream_handler to the logger
    logger.addHandler(stream_handler)

    # Only change the logging-level if it's above what we want it to be
    if logger.getEffectiveLevel() > noca_logging_level:
        logger.setLevel(noca_logging_level)
