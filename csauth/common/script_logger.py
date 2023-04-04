""" Factories for creating logging.Logger instances.
"""


import datetime as dt
import logging
from logging import (
    NullHandler,        # For test environment
    StreamHandler,      # For live environemnt
    FileHandler,        # "   "    "
)
import os.path

import settings

def _get_logging_formatter(include_name=True) -> logging.Formatter:
    return logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
        if include_name
        else
        '%(asctime)s %(levelname)s %(message)s'
    )

def _get_report_formatter() -> logging.Formatter:
    return logging.Formatter(
        '%(levelname)s %(message)s'
    )

def get_debug_console_logger(logger_name: str = None) -> logging.Logger:
    logger = logging.getLogger(logger_name if logger_name else __name__)
    logger.setLevel(logging.DEBUG)
    handler = NullHandler() if settings.IS_TEST else StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(_get_logging_formatter(include_name=False))
    logger.addHandler(handler)
    logger.debug("debug console logger instantiated")
    return logger

def get_task_logger(logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Console logging
    console_handler = NullHandler() if settings.IS_TEST else logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(_get_logging_formatter(include_name=False))
    logger.addHandler(console_handler)

    # Log file
    log_file_handler = NullHandler() if settings.IS_TEST else FileHandler(
        os.path.join(
            settings.LOGS_DIR,
            dt.datetime.now().strftime(
                '%Y-%m-%d_%H%M%S'
            ) + '_' + logger_name + '.log',
        )
    )
    log_file_handler.setLevel(logging.INFO)
    log_file_handler.setFormatter(_get_logging_formatter())
    logger.addHandler(log_file_handler)

    # Task Report
    report_file_handler = NullHandler() if settings.IS_TEST else FileHandler(
        os.path.join(
            settings.LOGS_DIR,
            dt.datetime.now().strftime(
                '%Y-%m-%d_%H%M%S'
            ) + '_' + logger_name + '.report',
        )
    )
    report_file_handler.setLevel(logging.INFO)
    report_file_handler.setFormatter(_get_report_formatter())
    logger.addHandler(report_file_handler)

    logger.debug("task logger instantiated")
    logger.debug(f"   .log file {getattr(log_file_handler, 'baseFilename', 'NONE')}")
    logger.debug(f".report file {getattr(report_file_handler, 'baseFilename', 'NONE')}")

    return logger
