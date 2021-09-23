"""Elastic search hook function."""

import os
import re
from datetime import datetime
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from typing import Any, AnyStr, Dict, NoReturn, Optional

from elasticsearch import Elasticsearch

from elasticlogger import utils
from elasticlogger.hooks import HookContext
from elasticlogger.ports.elasticsearch import get_instance

from .errors import ESConfigurationError, ESEmptyIndexError, ESEmptyUrlError


class ElasticSearch:
    """Elastic Search hook implementation.

    :type url: str
    :param url: Elasticsearch cluster endpoint

    :type index: str
    :param index: Index of ES where will be stored the logs

    :param **kwargs: All Elasticsearch object params
    """

    def __init__(self, url: Optional[AnyStr] = None, index: Optional[AnyStr] = None, **kwargs: Dict[AnyStr, Any]):
        self.__url: AnyStr = url if url else os.getenv('ELASTICSEARCH_URL', None)
        self.__index: AnyStr = index if index else os.getenv('ELASTICSEARCH_INDEX', None)
        self.__kwargs: Dict[AnyStr, Any] = kwargs
        self.__client: Elasticsearch = self.__init_client()

    def __call__(self, context: HookContext) -> NoReturn:
        """Main execution of the Elastic Search Hook.

        :param context: Current log record context
        """

        if not self.__check_level(context.level, context.logger_level):
            return

        document = {
            "@timestamp": datetime.now(),
            "@message": context.message,
            "level": utils.get_level_name(context.level),
            "name": context.logger_name,
        }

        document.update(context.extra_data)
        document = self.__clean_metadata_keys(document)

        self.__client.index(index=self.__index, body=document)

    def __init_client(self) -> Elasticsearch:
        """Create new client instance to stream logs.

        :return Elasticsearch: New client instance
        """

        if self.__url is None:
            raise ESEmptyUrlError('Empty Elasticsearch server.')

        if self.__index is None:
            raise ESEmptyIndexError('Empty Elasticsearch index.')

        try:
            return get_instance(self.__url, **self.__kwargs)
        except Exception as error:
            raise ESConfigurationError('Error creating Elasticsearch client instance') from error

    @staticmethod
    def __clean_metadata_keys(document: Dict[AnyStr, Any]) -> Dict[AnyStr, Any]:
        """Remove all keys of a document that start with underscore to not be confused with metadata keys

        :param document: Full document data

        :return Dict[AnyStr, Any]: Cleaned document with out metadata keys
        """

        new_document = document.copy()

        for key in document.keys():
            if re.search("^_", key) is not None:
                del new_document[key]

        return new_document

    @staticmethod
    def __check_level(log_level: int, logger_level: int) -> bool:
        """Validate if the configured level and the given logs are valid to stream to Elasticsearch

        :param log_level: current log level of the ES document
        :param logger_level: Global logger level

        :return bool: Boolean assertion
        """

        if log_level == DEBUG and logger_level == DEBUG:
            return True

        if log_level == INFO and logger_level in {DEBUG, INFO}:
            return True

        if log_level == WARNING and logger_level in {DEBUG, INFO, WARNING}:
            return True

        if log_level == ERROR and logger_level in {DEBUG, INFO, WARNING, ERROR}:
            return True

        if log_level == CRITICAL and logger_level in {DEBUG, INFO, WARNING, ERROR, CRITICAL}:
            return True

        return False
