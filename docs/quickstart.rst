Quick Start
===========

Basic config
------------

ElasticLogger use the standard python logging package and the python_json_logger package
to get a standardized logger that can be compatible with elastic search and Sentry.

The way to create a simple logger is by following the next example:

.. code-block:: python

    import logging
    from elasticlogger import Logger

    logger = Logger("test-logger", level=logging.DEBUG)

This will create a logger instance with DEBUG level and you can simply log like this:

.. code-block:: python

    logger.debug("test logger message")
    # {"message": "test logger message", "levelname": "DEBUG", "name": "test-logger"}

ElasticSearch Integration
-------------------------

To enable the ElasticSearch integration you need to call the next function with params
`url` and `index`, where endpoint is the elastic cluster url and the index will be
the default index where the logs will be stored.

.. code-block:: python

    # Setup the ElasticSearch endpoint of your cluster and the default index
    logger.enable_elastic(url="https://elastic-cluster.com", index="test-index")

    # You can simply call the function and the data will be take from the env vars
    # ELASTICSEARCH_URL and ELASTICSEARCH_INDEX
    logger.enable_elastic()
