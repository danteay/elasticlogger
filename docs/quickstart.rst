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
    # {"asctime": "2021-09-23 20:35:21,261", "levelname": "DEBUG", "name": "test-logger", "message": "test logger message"}
