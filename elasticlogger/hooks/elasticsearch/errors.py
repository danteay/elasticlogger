"""Elastic search specific errors."""


class ESEmptyIndexError(Exception):
    """Error that is thrown when the Elasticlogger configuration doesn't have a valid index to stream the logs"""


class ESEmptyUrlError(Exception):
    """Error that is thrown when Elasticlogger configuration can't find a valid ES URL"""


class ESConfigurationError(Exception):
    """Error that is thrown by a miss configuration on the elasticsearch.Elasticsearch object"""
