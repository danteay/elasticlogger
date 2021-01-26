"""Logger implementation"""

import json
import os
import logging
import traceback
import sys

from datetime import datetime
from elasticsearch import Elasticsearch
from pythonjsonlogger import jsonlogger

import certifi
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger

from .context import Context
from .errors import ESEmptyIndexError, ESEmptyUrlError, ESConfigurationError, SentryEmptyUrlError


class Logger:
    """
    This is the main API class to interact with the JSON logs. Has the needed methods to log information as
    DEBUG, INFO, WARNING and ERROR levels with specific features like adding errors with tracing data,
    communicate events with with Sentry monitoring spaces and the core of this integration, stream your logs
    as Elasticsearch documents in a specific index.

    :param name: Logger name
    :param level: Logger level (Def: DEBUG)
    :param fmt: Log format fields (Def: %(asctime) %(levelname) %(name) %(message))
    """

    _RESERVED_KEYS = ["name", "level", "asctime", "levelname", "message", "@message", "@timestamp"]

    def __init__(self, name: str, level: int = None, fmt: str = None):
        self.extra = {}
        self.elastic = None
        self.sentry = None
        self.elastic_index = None
        self.level = level
        self.context = Context()
        self.logger = self._create_logger(name=name, level=level, fmt=fmt)

    def enable_elastic(self, url: str = None, index: str = None, **kwargs):
        """
        Enable ElasticSearch integration to stream logs. If you don't set endpoint and index
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
        """

        if len(kwargs.keys()) > 0 and "hosts" in kwargs:
            del kwargs["hosts"]

        endpoint = url if url else os.getenv("ELASTICSEARCH_URL", None)

        if not endpoint:
            raise ESEmptyUrlError()

        self.elastic_index = index if index else os.getenv("ELASTICSEARCH_INDEX", None)

        if not self.elastic_index:
            raise ESEmptyIndexError("Can't find a valid ES index")

        try:
            if len(kwargs.keys()) > 0:
                if "hosts" in kwargs:
                    del kwargs["hosts"]

                self.elastic = Elasticsearch(hosts=endpoint, **kwargs)
            else:
                self.elastic = Elasticsearch(hosts=endpoint, use_ssl=True, verify_certs=True, ca_certs=certifi.where())
        except Exception as error:
            raise ESConfigurationError() from error

    def enable_sentry(
        self,
        url: str = None,
        integrations: [object] = None,
        level: int = logging.DEBUG,
        event_level: int = logging.ERROR
    ):
        """
        Enable Sentry integration for realtime issue monitoring. If you don't set the endpoint
        field it will be set from the env ver SENTRY_URL. On the integrations field you can set a
        list of objects from the sentry_sdk.integrations package to be implemented.

        :param url: Sentry project endpoint
        :param integrations: List of sentry_sdk.integrations objects
        :param level: Capture info and above as breadcrumbs
        :param event_level: Register events when this level is use

        :raise SentryEmptyUrlError: Configuration can find a provided URL or configured env var SENTRY_URL
        """

        endpoint = url if url else os.getenv("SENTRY_URL", None)

        if not endpoint:
            raise SentryEmptyUrlError()

        sentry_logging = LoggingIntegration(
            level=level,
            event_level=event_level,
        )

        base_integrations = [sentry_logging]

        if integrations is not None:
            integrations = integrations + base_integrations

        ignore_logger("root")
        self.sentry = sentry_sdk.init(endpoint, integrations=integrations)

    def fields(self, fields: dict):
        """
        Add multiple extra fields to the json log string

        :param fields: Extra fields to add in the json log

        :return: Self instance
        """

        if not isinstance(fields, dict):
            return self

        self.extra.update(fields)
        return self

    def field(self, name: str, value):
        """
        Add a single field to the json log string

        :param name: New key name for the field
        :param value: Value of the field (if it's an object needs to be json serializable)

        :return: Self instance
        """

        self.extra.update({name: value})
        return self

    def debug(self, message: str):
        """
        Print a debug log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: Log message
        """

        self.logger.debug(message, extra=self._get_extra_data())

        if self.level <= logging.DEBUG:
            self._ensure_elastic(message, "DEBUG")

    def debugf(self, message: str, *args, **kwargs):
        """
        Print a debug log with all extra fields saved and formatted message. The fields will be
        cleaned after the logs are send

        :param message: Log message
        """

        message = message.format(*args, **kwargs)
        self.debug(message)

    def info(self, message: str):
        """
        Print an info log with all extra fields saved. The fields will be cleaned after
        the logs are send

        :param message: Log message
        """

        self.logger.info(message, extra=self._get_extra_data())

        if self.level <= logging.INFO:
            self._ensure_elastic(message, "INFO")

    def infof(self, message: str, *args, **kwargs):
        """
        Print a info log with all extra fields saved and formatted message. The
        fields will be cleaned after the logs are send

        :param message: Log message
        """

        message = message.format(*args, **kwargs)
        self.info(message)

    def warning(self, message: str):
        """
        Print a warning log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: Log message
        """

        self.logger.warning(message, extra=self._get_extra_data())

        if self.level <= logging.WARNING:
            self._ensure_elastic(message, "WARNING")

    def warningf(self, message: str, *args, **kwargs):
        """
        Print a warning log with all extra fields saved and formatted message. The fields will be
        cleaned after the logs are send

        :param message: Log message
        """

        message = message.format(*args, **kwargs)
        self.warning(message)

    def error(self, message: str, error=None):
        """
        Print an error log with all extra fields saved, and with an specific error field. The
        fields will be cleaned after the logs are send

        :param message: Log message
        :param error: Exception or specific error message
        """

        self.err(error)
        self.logger.error(message, extra=self._get_extra_data())

        if self.level <= logging.ERROR:
            self._ensure_elastic(message, "ERROR")

    def errorf(self, error, message: str, *args, **kwargs):
        """
        Print an error log with all extra fields saved and formatted message, and with an specific
        error field. The fields will be cleaned after the logs are send

        :param message: Log message
        :param error: Exception or specific error message
        """

        message = message.format(*args, **kwargs)
        self.error(message=message, error=error)

    def err(self, error):
        """
        Method used to specify some error data on extra fields without logging it as an error event

        :param error: Error information

        :return: Self instance
        """

        if isinstance(error, Exception):
            error = error.args[0]

        self.extra.update({"error": error})

        exc_type, exc_value, exc_tb = sys.exc_info()
        trace_length = len(traceback.format_exception(exc_type, exc_value, exc_tb))

        if trace_length > 1:
            trace = traceback.format_exc()
            self.extra.update({"trace": trace})

        return self

    def _ensure_elastic(self, message: str, level: str):
        """
        Ensure elastic search synchronization, by checking configuration and collecting data

        :param message: Principal message of the log
        :param level: Log level
        """

        if not self.elastic:
            return

        doc = {
            "@timestamp": datetime.now(),
            "@message": message,
            "level": level,
            "name": self.logger.name,
        }

        doc.update(self.extra)

        if "error" in doc:
            doc["error"] = str(doc["error"])

        self.elastic.index(index=self.elastic_index, body=doc)

    def _get_extra_data(self):
        """
        Build extra data from context and local log data

        :return: Dict with all log data
        """

        with self.context as context:
            data = self.extra
            data.update(context.data)
            self.extra = {}

            return self._clean_reserved_keys(data)

    def _clean_reserved_keys(self, extra_data: dict):
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

    @staticmethod
    def _default_translate(obj):
        """
        Default transformation for any not known object

        :param obj: Object to be transformed

        :return: String transformation
        """

        return str(obj)

    def _create_logger(self, name: str, level: int = None, fmt: str = None):
        """
        Configure python JSON logger

        :param name: Name of the logger
        :param level: Logging level from `logging` library
        :param fmt: standard logger format
        """

        logger = logging.getLogger(name)
        level = logging.DEBUG if not level else level
        fmt = u"%(asctime) %(levelname) %(name) %(message)" if not fmt else fmt

        formatter = jsonlogger.JsonFormatter(fmt, json_default=self._default_translate, json_encoder=json.JSONEncoder)

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(level)

        return logger
