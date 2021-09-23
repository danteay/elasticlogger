"""Base logger definition."""

import logging
from abc import abstractmethod
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from typing import Any, AnyStr, Dict, NoReturn, Optional

from pythonjsonlogger import jsonlogger

from elasticlogger import utils
from elasticlogger.types.context import Context
from elasticlogger.types.json_encoder import LoggerJSONEncoder


class BaseLogger:
    """Base Logger class that holds all basic functionality to manage json log formatting
    and processing.

    :type name: str
    :param name: Logger name

    :type level: int
    :param level: Logger level (Def: DEBUG)

    :type fmt: str
    :param fmt: Log format fields (Def: %(asctime) %(levelname) %(name) %(message))
    """

    RESERVED_KEYS = ["name", "level", "asctime", "levelname", "message"]

    def __init__(self, name: AnyStr, level: Optional[int] = None, fmt: Optional[AnyStr] = None):
        self.__extra = {}
        self.__level = level
        self.__name = name
        self.__context = Context()
        self.__logger = self.__create_logger(name=name, level=level, fmt=fmt)

    @property
    def level(self):
        """Return level"""
        return self.__level

    @property
    def name(self):
        """Get property value"""
        return self.__name

    @property
    def context(self):
        """Return logger persistent context"""
        return self.__context

    @property
    def logger(self):
        """Return logger instance from logging package."""
        return self.__logger

    def set_level(self, level: int) -> NoReturn:
        """Change the configured level of the logger."""

        self.__level = level
        self.__logger.setLevel(level)

    def fields(self, fields: Dict[AnyStr, Any]):
        """Add multiple extra fields to the json log string

        :param fields: Extra fields to add in the json log
        :return: Self instance
        """

        if not isinstance(fields, dict):
            return self

        self.__extra.update(fields)
        return self

    def field(self, name: AnyStr, value: Any):
        """Add a single field to the json log string

        :param name: New key name for the field
        :param value: Value of the field (if it's an object needs to be json serializable)

        :return: Self instance
        """

        self.__extra.update({name: value})
        return self

    def err(self, error: Any):
        """Method used to specify some error data on extra fields without logging it as an error event

        :param error: Error information

        :return: Self instance
        """

        error_info = utils.get_error_info(error)
        self.__extra.update(error_info)

        return self

    def debug(self, message: AnyStr, *args, **kwargs) -> NoReturn:
        """Print a debug log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: Log message
        """

        self.log(DEBUG, message, *args, **kwargs)

    def info(self, message: AnyStr, *args, **kwargs) -> NoReturn:
        """Print an info log with all extra fields saved. The fields will be cleaned after
        the logs are send

        :param message: Log message
        """

        self.log(INFO, message, *args, **kwargs)

    def warning(self, message: AnyStr, *args, **kwargs) -> NoReturn:
        """Print a warning log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: Log message
        """

        self.log(WARNING, message, *args, **kwargs)

    def error(self, message: AnyStr, *args, **kwargs) -> NoReturn:
        """Print an error log with all extra fields saved, and with an specific error field. The
        fields will be cleaned after the logs are send

        :param message: Log message
        """

        self.log(ERROR, message, *args, **kwargs)

    def critical(self, message: AnyStr, *args, **kwargs) -> NoReturn:
        """Print a fatal error log with all extra fields saved, and with an specific error field. The
        fields will be cleaned after the logs are send

        :param message: Log message
        """

        self.log(CRITICAL, message, *args, **kwargs)

    @abstractmethod
    def log(self, level: int, message: AnyStr, *args, **kwargs) -> NoReturn:
        """Dynamically log data to a specific level.

        :param level: Level of the log message
        :param message: Message to be logged
        """

        raise NotImplementedError('Method is not implemented')

    def _get_extra_data(self) -> Dict[AnyStr, Any]:
        """Build extra data from context and local log data

        :return Dict[AnyStr, Any]: Dict with all log data
        """

        with self.__context as context:
            data = context.data

        data.update(self.__extra)
        self.__extra.clear()

        return self.__clean_reserved_keys(data)

    @staticmethod
    def __create_logger(name: AnyStr, level: int = None, fmt: AnyStr = None) -> logging.Logger:
        """Configure python JSON logger

        :param name: Name of the logger
        :param level: Logging level from `logging` library
        :param fmt: standard logger format

        :return logging.Logger: New logger instance
        """

        logger = logging.getLogger(name)
        level = logging.DEBUG if not level else level
        fmt = "%(asctime) %(levelname) %(name) %(message)" if not fmt else fmt

        formatter = jsonlogger.JsonFormatter(fmt, json_encoder=LoggerJSONEncoder)

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(level)

        return logger

    def __clean_reserved_keys(self, extra_data: Dict[AnyStr, Any]) -> Dict[AnyStr, Any]:
        """Delete logger reserved keys to avoid override data

        :param extra_data: Data that will be included as extra fields on the logs

        :return Dict[AnyStr, Any]: Clean extra data without the reserved keys
        """

        extra_keys = extra_data.keys()

        for key in self.RESERVED_KEYS:
            if key in extra_keys:
                extra_data.pop(key)

        return extra_data
