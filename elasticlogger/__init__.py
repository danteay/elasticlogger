"""Python custom logger"""

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
    """Custom logger that interact with python_json_logger and elastic search

    :param name: (str) Logger name
    :param level: Optional(str) Logger level (Def: DEBUG)
    :param fmt: Optional(str) Log format fields (Def: %(asctime) %(levelname) %(name) %(message))
    """

    def __init__(self, name, level=None, fmt=None):
        self.extra = {}
        self.elastic = None
        self.sentry = None
        self.index = None
        self.logger = logging.getLogger(name)

        level = logging.DEBUG if not level else level
        handler = logging.StreamHandler()

        fmt = u"%(asctime) %(levelname) %(name) %(message)" if not fmt else fmt

        handler.setFormatter(jsonlogger.JsonFormatter(fmt))

        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    def enable_elastic(self, endpoint=None, index=None):
        """Enable ElasticSearch integration to stream logs. If you don't set endpoint and index
        configurations this will try to get the configuration form the environment variables
        ELASTIC_SEARCH_ENDPOINT and ELASTIC_SEARCH_INDEX

        :param endpoint: Optional(str) ElasticSearch cluster endpoint
        :param index: Optional(str) ElasticSearch index where the logs will be streamed
        """
        endpoint = endpoint if endpoint else os.getenv("ELASTIC_SEARCH_ENDPOINT")

        if not endpoint:
            return

        self.elastic = Elasticsearch(
            endpoint, use_ssl=True, verify_certs=True, ca_certs=certifi.where()
        )
        self.index = index if index else os.getenv("ELASTIC_SEARCH_INDEX")

    def enable_sentry(self, endpoint=None, integrations=None):
        """Enable Sentry integration for realtime issue monitoring. If you don't set the endpoint
        field it will be set from the env ver SENTRY_URL. On the integrations field you can set a
        list of objects from the sentry_sdk.integrations package to be implemented.

        :param endpoint: Optional(str) Sentry project endpoint
        :param integrations: Optional(list) List of sentry_sdk.integrations objects
        """

        endpoint = endpoint if endpoint else os.getenv("SENTRY_URL")

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
        """Add multiple extra fields to the json log string

        :param fields: (dict) Extra fields to add in the json log
        :return: (self)
        """

        if not isinstance(fields, dict):
            return self

        self.extra.update(fields)
        return self

    def field(self, name, value):
        """Add a single field to the json log string

        :param name: (str) New key name for the field
        :param value: (Any) Value of the field (if it's an object needs to be json serializable)
        :return: (self)
        """

        self.extra.update({name: value})
        return self

    def debug(self, message):
        """Print a debug log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: (str) Log message
        """

        self.logger.debug(message, extra=self.extra)
        self._ensure_elastic(message, "DEBUG")
        self.extra = {}

    def info(self, message):
        """Print an info log with all extra fields saved. The fields will be cleaned after the
        logs are send

        :param message: (str) Log message
        """

        self.logger.info(message, extra=self.extra)
        self._ensure_elastic(message, "INFO")
        self.extra = {}

    def warning(self, message):
        """Print a warning log

        :param message: (str) Log message
        """

        self.logger.warning(message, extra=self.extra)
        self._ensure_elastic(message, "WARNING")
        self.extra = {}

    def error(self, message, error=None):
        """Print an error log with all extra fields saved, and with an specific error field. The
        fields will be cleaned after the logs are send

        :param message: (str) Log message
        :param error: Optional(Any) Exception or specific error message
        """
        trace = None

        if error:
            trace = traceback.format_exc()
            self.extra.update({"error": str(error), "trace": trace})

        self.logger.error(message, extra=self.extra)
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
