
import logging

def _get_logging_formatter(include_name=True) -> logging.Formatter:
    return logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
        if include_name
        else
        '%(asctime)s %(levelname)s %(message)s'
    )

def get_debug_console_logger(logger_name: str = None) -> logging.Logger:
    logger = logging.getLogger(logger_name if logger_name else __name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(_get_logging_formatter(include_name=False))
    logger.addHandler(handler)
    logger.debug("debug console logger instantiated")
    return logger
