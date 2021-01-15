"""Logger implementation"""

import os
import logging
import traceback

from datetime import datetime
from elasticsearch import Elasticsearch
from pythonjsonlogger import jsonlogger

import certifi
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger


class Logger:
    """
    Custom logger that interact with python_json_logger and elastic search

    :param name: (str) Logger name
    :param level: Optional(str) Logger level (Def: DEBUG)
    :param fmt: Optional(str) Log format fields (Def: %(asctime) %(levelname) %(name) %(message))
    """

    def __init__(self, name, level=None, fmt=None):
        self.extra = {}
        self.elastic = None
        self.sentry = None
        self.index = None
        self.level = level
        self.logger = logging.getLogger(name)

        level = logging.DEBUG if not level else level
        handler = logging.StreamHandler()

        fmt = u"%(asctime) %(levelname) %(name) %(message)" if not fmt else fmt

        handler.setFormatter(jsonlogger.JsonFormatter(fmt))

        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    def enable_elastic(self, url=None, index=None, **kwargs):
        """
        Enable ElasticSearch integration to stream logs. If you don't set endpoint and index
        configurations this will try to get the configuration form the environment variables
        ELASTIC_SEARCH_URL and ELASTIC_SEARCH_INDEX

        :param url: Optional(str) ElasticSearch cluster endpoint
        :param index: Optional(str) ElasticSearch index where the logs will be streamed
        :param kwargs: Elasticsearch object configuration args. if ani other is setup this will be use to config
        Elastic search object instead of default config
        """
        endpoint = url if url else os.getenv("ELASTIC_SEARCH_URL")

        if not endpoint:
            return

        if len(kwargs) > 0:
            if "hosts" in kwargs:
                del kwargs["hosts"]

            self.elastic = Elasticsearch(hosts=endpoint, **kwargs)
        else:
            self.elastic = Elasticsearch(hosts=endpoint, use_ssl=True, verify_certs=True, ca_certs=certifi.where())

        self.index = index if index else os.getenv("ELASTIC_SEARCH_INDEX")

    def enable_sentry(self, url=None, integrations=None):
        """
        Enable Sentry integration for realtime issue monitoring. If you don't set the endpoint
        field it will be set from the env ver SENTRY_URL. On the integrations field you can set a
        list of objects from the sentry_sdk.integrations package to be implemented.

        :param url: Optional(str) Sentry project endpoint
        :param integrations: Optional(list) List of sentry_sdk.integrations objects
        """

        endpoint = url if url else os.getenv("SENTRY_URL")

        if not endpoint:
            return

        sentry_logging = LoggingIntegration(
            level=logging.DEBUG,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )

        base_integrations = [sentry_logging]

        if integrations is not None:
            integrations = integrations + base_integrations

        ignore_logger("root")
        self.sentry = sentry_sdk.init(endpoint, integrations=integrations)

    def fields(self, fields):
        """
        Add multiple extra fields to the json log string

        :param fields: (dict) Extra fields to add in the json log
        :return: (self)
        """

        if not isinstance(fields, dict):
            return self

        self.extra.update(fields)
        return self

    def field(self, name, value):
        """
        Add a single field to the json log string

        :param name: (str) New key name for the field
        :param value: (Any) Value of the field (if it's an object needs to be json serializable)
        :return: (self)
        """

        self.extra.update({name: value})
        return self

    def debug(self, message):
        """
        Print a debug log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: (str) Log message
        """

        self.logger.debug(message, extra=self.extra)

        if self.level <= logging.DEBUG:
            self._ensure_elastic(message, "DEBUG")

        self.extra = {}

    def info(self, message):
        """
        Print an info log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: (str) Log message
        """

        self.logger.info(message, extra=self.extra)

        if self.level <= logging.INFO:
            self._ensure_elastic(message, "INFO")

        self.extra = {}

    def warning(self, message, error=None):
        """
        Print a warning log

        :param message: (str) Log message
        :param error: (Any|Exception) Possible handled error that should be logged
        """

        trace = None

        if error:
            trace = traceback.format_exc()

            if isinstance(error, Exception):
                error = error.args[0]
            else:
                error = str(error)

            self.extra.update({"error": error, "trace": trace})

        self.logger.warning(message, extra=self.extra)

        if self.level <= logging.WARNING:
            self._ensure_elastic(message, "WARNING", error=error, trace=trace)

        self.extra = {}

    def error(self, message, error=None):
        """
        Print an error log with all extra fields saved, and with an specific error field. The
        fields will be cleaned after the logs are send

        :param message: (str) Log message
        :param error: Optional(Any) Exception or specific error message
        """

        trace = None

        if error:
            trace = traceback.format_exc()

            if isinstance(error, Exception):
                error = error.args[0]
            else:
                error = str(error)

            self.extra.update({"error": error, "trace": trace})

        self.logger.error(message, extra=self.extra)

        if self.level <= logging.ERROR:
            self._ensure_elastic(message, "ERROR", error, trace)

        self.extra = {}

    def _ensure_elastic(self, message, level, error=None, trace=None):
        """Ensure elastic search synchronization, by checking configuration and collecting data

        :param message: (str) Principal message of the log
        :param level: (str) Log level
        :param error: Optional(Any) Error to be logged
        :param trace: Optional(str) Last error trace
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

        if error:
            doc.update({"error": str(error)})

        if trace:
            doc.update({"trace": trace})

        self.elastic.index(index=self.index, body=doc)
