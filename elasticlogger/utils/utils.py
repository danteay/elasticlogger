"""Utils that can be used across all files."""

import logging
import sys
import traceback
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from typing import Any, AnyStr, Callable, Dict

from elasticlogger.errors import InvalidLogLevel


def get_level_name(level: int):
    """Return level name from logging package levels

    :param level: Logging level

    :raise InvalidLogLevel: For an invalid level value

    :return int: String name
    """

    levels = {
        DEBUG: 'DEBUG',
        INFO: 'INFO',
        WARNING: 'WARNING',
        ERROR: 'ERROR',
        CRITICAL: 'CRITICAL',
    }

    level_name = levels.get(level, None)

    if level_name is None:
        raise InvalidLogLevel(f"Invalid logging level detected: [{level}]")

    return level_name


def get_logging_method(level: int, logger: logging.Logger) -> Callable:
    """Return logging method from an instance of a logger

    :param level: Logging level
    :param logger: Current instance of a Logger object

    :raise InvalidLogLevel: For an invalid level value

    :return int: String name
    """

    methods = {
        DEBUG: logger.debug,
        INFO: logger.info,
        WARNING: logger.warning,
        ERROR: logger.error,
        CRITICAL: logger.critical
    }

    log_method = methods.get(level, None)

    if log_method is None:
        raise InvalidLogLevel(f'Invalid logging level: [{level}]')

    return log_method


def get_error_info(error: Any) -> Dict[AnyStr, Any]:
    """Extract error information from a given error object.

    :param error: Error information

    :return Dict[AnyStr, Any]: Extracted error information
    """

    error_info = {}

    if error is None:
        return error_info

    if isinstance(error, Exception):
        error_info['error'] = error.args[0]
    else:
        error_info['error'] = str(error)

    exc_type, exc_value, exc_tb = sys.exc_info()
    trace_length = len(traceback.format_exception(exc_type, exc_value, exc_tb))

    if trace_length > 1:
        trace = traceback.format_exc()
        error_info["trace"] = trace

    return error_info
