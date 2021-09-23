"""Elastic search actions."""

from typing import Any, AnyStr

import certifi
from elasticsearch import Elasticsearch

from elasticlogger.types.json_encoder import ElasticJSONEncoder


def get_instance(endpoint: AnyStr, **kwargs: Any) -> Elasticsearch:
    """Generate an Elastic search instance to stream all logs.

    :param endpoint: ElasticSearch cluster endpoint
    :param kwargs: All Elasticsearch object params

    :return Elasticsearch: New instance
    """

    if kwargs is None:
        kwargs = {}

    keys = kwargs.keys()

    if 'use_ssl' not in keys:
        kwargs['use_ssl'] = True

    if 'verify_certs' not in keys:
        kwargs['verify_certs'] = True

    if 'ca_certs' not in keys:
        kwargs['ca_certs'] = certifi.where()

    if "hosts" in kwargs:
        del kwargs["hosts"]

    return Elasticsearch(hosts=endpoint, serializer=ElasticJSONEncoder(), **kwargs)
