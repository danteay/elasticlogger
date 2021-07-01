"""Logger implementation"""

import logging
import os
import re
import sys
import traceback
from datetime import datetime
from logging import DEBUG, ERROR, FATAL, INFO, WARNING
from typing import Any, AnyStr, Dict, NoReturn, Optional

from pythonjsonlogger import jsonlogger

import elasticlogger.elastic as elastic

from .context import Context
from .errors import (ESConfigurationError, ESEmptyIndexError, ESEmptyUrlError, InvalidLogLevel)
from .json_encoder import LoggerJSONEncoder


class Logger:
    """This is the main API class to interact with the JSON logs. Has the needed methods to log information as
    DEBUG, INFO, WARNING and ERROR levels with specific features like adding errors with tracing data,
    communicate events with with Sentry monitoring spaces and the core of this integration, stream your logs
    as Elasticsearch documents in a specific index.

    :param name: Logger name
    :param level: Logger level (Def: DEBUG)
    :param fmt: Log format fields (Def: %(asctime) %(levelname) %(name) %(message))
    """

    _RESERVED_KEYS = ["name", "level", "asctime", "levelname", "message", "@message", "@timestamp"]

    def __init__(self, name: AnyStr, level: Optional[int] = None, fmt: Optional[AnyStr] = None):
        self._extra = {}
        self._name = name
        self._elastic = None
        self._elastic_index = None
        self._level = level
        self._context = Context()
        self._logger = self._create_logger(name=name, level=level, fmt=fmt)

    def set_level(self, level: int) -> NoReturn:
        """Change the configured level of the logger."""

        self._level = level
        self._logger.setLevel(level)

    @property
    def level(self):
        """Return level"""
        return self._level

    @property
    def name(self):
        """Get property value"""
        return self._name

    @property
    def context(self):
        """Return logger persistent context"""
        return self._context

    @property
    def logger(self):
        """Return logger instance from logging package."""
        return self._logger

    def enable_elastic(self, url: Optional[AnyStr] = None, index: Optional[AnyStr] = None, **kwargs: Any) -> NoReturn:
        """Enable ElasticSearch integration to stream logs. If you don't set endpoint and index
        configurations this will try to get the configuration form the environment variables
        ELASTICSEARCH_URL and ELASTICSEARCH_INDEX

        :param url: ElasticSearch cluster endpoint
        :param index: ElasticSearch index where the logs will be streamed
        :param kwargs: This is a compilation of the elasticsearch.Elasticsearch object params
            that creates the main connection object. By default if Kwargs are not set, the object
            will be configured with the next params:

                use_ssl=True
                verify_certs=True
                ca_certs=certifi.where()

            If any Kwarg is set, default configuration will be omitted and Kwargs will be used
            in place

        :raises ESEmptyUrlError: When the url param and the ELASTICSEARCH_URL env var are empty
        :raises ESEmptyIndexError: When the index param and the ELASTICSEARCH_INDEX env var are empty
        :raises ESConfigurationError: When the Elasticsearch object raise a configuration error
        """

        endpoint = url if url else os.getenv("ELASTICSEARCH_URL", None)

        if not endpoint:
            raise ESEmptyUrlError()

        self._elastic_index = index if index else os.getenv("ELASTICSEARCH_INDEX", None)

        if not self._elastic_index:
            raise ESEmptyIndexError("Can't find a valid ES index")

        try:
            self._elastic = elastic.get_instance(endpoint, **kwargs)
        except Exception as error:
            raise ESConfigurationError() from error

    def fields(self, fields: Dict[AnyStr, Any]):
        """Add multiple extra fields to the json log string

        :param fields: Extra fields to add in the json log
        :return: Self instance
        """

        if not isinstance(fields, dict):
            return self

        self._extra.update(fields)
        return self

    def field(self, name: AnyStr, value: Any):
        """Add a single field to the json log string

        :param name: New key name for the field
        :param value: Value of the field (if it's an object needs to be json serializable)
        :return: Self instance
        """

        self._extra.update({name: value})
        return self

    def debug(self, message: AnyStr):
        """Print a debug log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: Log message
        """

        self._logger.debug(message, extra=self._get_extra_data())
        self._ensure_elastic(message, DEBUG)
        self._extra = {}

    def info(self, message: AnyStr):
        """Print an info log with all extra fields saved. The fields will be cleaned after
        the logs are send

        :param message: Log message
        """

        self._logger.info(message, extra=self._get_extra_data())
        self._ensure_elastic(message, INFO)
        self._extra = {}

    def warning(self, message: AnyStr):
        """
        Print a warning log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: Log message
        """

        self._logger.warning(message, extra=self._get_extra_data())
        self._ensure_elastic(message, WARNING)
        self._extra = {}

    def error(self, message: AnyStr, error: Any = None):
        """
        Print an error log with all extra fields saved, and with an specific error field. The
        fields will be cleaned after the logs are send

        :param message: Log message
        :param error: Exception or specific error message
        """

        self.err(error)
        self._logger.error(message, extra=self._get_extra_data())
        self._ensure_elastic(message, ERROR)

        self._extra = {}

    def critical(self, message: AnyStr, error: Any = None):
        """Print a fatal error log with all extra fields saved, and with an specific error field. The
        fields will be cleaned after the logs are send

        :param message: Log message
        :param error: Exception or specific error message
        """

        self.err(error)
        self._logger.fatal(message, extra=self._get_extra_data())
        self._ensure_elastic(message, FATAL)
        self._extra = {}

    def err(self, error: Any):
        """
        Method used to specify some error data on extra fields without logging it as an error event

        :param error: Error information

        :return: Self instance
        """

        if error is None:
            return self

        if isinstance(error, Exception):
            error = error.args[0]
        else:
            error = str(error)

        self._extra["error"] = error

        exc_type, exc_value, exc_tb = sys.exc_info()
        trace_length = len(traceback.format_exception(exc_type, exc_value, exc_tb))

        if trace_length > 1:
            trace = traceback.format_exc()
            self._extra["trace"] = trace

        return self

    def _ensure_elastic(self, message: AnyStr, level: int):
        """
        Ensure elastic search synchronization, by checking configuration and collecting data

        :param message: Principal message of the log
        :param level: ES document level for the log
        """

        if not self._elastic or not self._check_level(level):
            return

        extra_fields = self._get_extra_data()

        document = {
            "@timestamp": datetime.now(),
            "@message": message,
            "level": self._get_level_name(level),
            "name": self._logger.name,
        }

        document.update(extra_fields)

        if "error" in document:
            document["error"] = str(document["error"])

        document = self._clean_metadata_keys(document)

        self._elastic.index(index=self._elastic_index, body=document)

    def _get_extra_data(self):
        """
        Build extra data from context and local log data

        :return: Dict with all log data
        """

        with self._context as context:
            data = self._extra
            data.update(context.data)

            return self._clean_reserved_keys(data)

    def _clean_reserved_keys(self, extra_data: Dict[AnyStr, Any]):
        """
        Delete logger reserved keys to avoid override data

        :param extra_data: Data that will be included as extra fields on the logs
        :return: Clean extra data without the reserved keys
        """

        extra_keys = extra_data.keys()

        for key in self._RESERVED_KEYS:
            if key in extra_keys:
                extra_data.pop(key)

        return extra_data

    def _check_level(self, level: int):
        """
        Validate if the configured level and the given logs are valid to stream to Elasticsearch
        :param level: current log level of the ES document
        :return: Boolean assertion
        """

        if level == logging.DEBUG and self._level == DEBUG:
            return True

        if level == logging.INFO and self._level in {DEBUG, INFO}:
            return True

        if level == logging.WARNING and self._level in {DEBUG, INFO, WARNING}:
            return True

        if level == logging.ERROR and self._level in {DEBUG, INFO, WARNING, ERROR}:
            return True

        if level == logging.FATAL and self._level in {DEBUG, INFO, WARNING, ERROR, FATAL}:
            return True

        return False

    @staticmethod
    def _get_level_name(level: int):
        """
        Return level name from logging package levels
        :param level: Logging level
        :return: String name
        """

        if level == DEBUG:
            return "DEBUG"

        if level == INFO:
            return "INFO"

        if level == WARNING:
            return "WARNING"

        if level == ERROR:
            return "ERROR"

        if level == FATAL:
            return "FATAL"

        raise InvalidLogLevel("Invalid logging level detected: [%d]" % level)

    @staticmethod
    def _create_logger(name: AnyStr, level: int = None, fmt: AnyStr = None) -> logging.Logger:
        """
        Configure python JSON logger

        :param name: Name of the logger
        :param level: Logging level from `logging` library
        :param fmt: standard logger format
        """

        logger = logging.getLogger(name)
        level = logging.DEBUG if not level else level
        fmt = u"%(asctime) %(levelname) %(name) %(message)" if not fmt else fmt

        formatter = jsonlogger.JsonFormatter(fmt, json_encoder=LoggerJSONEncoder)

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(level)

        return logger

    @staticmethod
    def _clean_metadata_keys(document: Dict[AnyStr, Any]):
        """
        Remove all keys of a document that start with underscore to not be confused with metadata keys
        :param document: Full document data
        :return: Cleaned document with out metadata keys
        """

        new_document = document.copy()

        for key in document.keys():
            if re.search("^_", key) is not None:
                del new_document[key]

        return new_document
