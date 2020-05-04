"""Python custom logger"""

import os
import logging
import traceback

from datetime import datetime
from elasticsearch import Elasticsearch
from pythonjsonlogger import jsonlogger

import certifi


class Logger:
    """Custom logger that interact with pythonjsonlogger and elastic search"""

    def __init__(self, name, level=None, fmt=None):
        self.extra = {}
        self.elastic = None
        self.index = None
        self.logger = logging.getLogger(name)

        level = logging.DEBUG if not level else level
        handler = logging.StreamHandler()

        fmt = u"%(message)%(levelname)%(name)" if not fmt else fmt

        handler.setFormatter(jsonlogger.JsonFormatter(fmt))

        self.logger.addHandler(handler)
        self.logger.setLevel(level)

    def enable_elastic(self, endpoint=None, index=None):
        """Enable elasticsearch integration to stream logs. If you don't set endpoint and index
        configurations this will try to get the configuration form the environment variables
        ELASTIC_SEARCH_ENDPOINT and ELASTIC_SEARCH_INDEX

        :param endpoint: (str) Elasticsearch cluster endpoint
        :param index: (str) Elasticsearch index where the logs will be streamed
        """
        endpoint = endpoint if endpoint else os.getenv("ELASTIC_SEARCH_ENPOINT")

        if not endpoint:
            return

        self.elastic = Elasticsearch(
            endpoint, use_ssl=True, verify_certs=True, ca_certs=certifi.where()
        )
        self.index = index if index else os.getenv("ELASTIC_SEARCH_INDEX")

    def fields(self, fields):
        """Add muntiple extra fields to the json log string

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
        :param value: (any) Value of the field (if it's an object needs to be json serializable)
        :return: (self)
        """

        self.extra.update({name: value})
        return self

    def debug(self, message):
        """Print a debug log with all extra fields saved. The fileds will be cleaned after the
        logs are send

        :param message: (str) Log message
        """

        self.logger.debug(message, extra=self.extra)
        self._ensure_elastic(message, "DEBUG")
        self.extra = {}

    def info(self, message):
        """Print an info log with all extra fields saved. The fileds will be cleaned after the
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
        fileds will be cleaned after the logs are send

        :param message: (str) Log message
        :param error: (any) Exception or specific error message
        """
        trace = None

        if error:
            trace = traceback.format_exc()
            self.extra.update({"error": str(error), "trace": trace})

        self.logger.error(message, extra=self.extra)
        self._ensure_elastic(message, "ERROR", error, trace)
        self.extra = {}

    def _ensure_elastic(self, message, level, error=None, trace=None):
        """Ensure elstic search syncronization, by checking configuration and colleting data

        :param message: (str) Principal message of the log
        :param level: (str) Log level
        :param error: (str) Error to be logged
        :param trace: (str) Last error trace
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
