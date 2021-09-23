Elasticsearch
==========================

.. toctree::
   :maxdepth: 5
   :caption: Contents:

   ./quickstart
   ./config_with_aws

Introduction
------------

Elasticlogger has a native implementation of the Elasticsearch driver to stream all your cluster
in a simply and effective way.

To start using this integration is as easy that you just need to call one method:

.. code-block:: python

    from elasticlogger import Logger
    from elasticlogger.hooks.elasticsearch import ElasticSearch

    logger = Logger('test', hooks=[ElasticSearch()])

    # Also can be added after Logger initialization
    logger.add_hook(ElasticSearch())

This will enable the elastic search integration by searching configs on the env vars `ELASTICSEARCH_URL`
and `ELASTICSEARCH_INDEX`.