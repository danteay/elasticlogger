Quick Satrt
===========

Elastic logger use the standard python logging package and the pythonjsonlogger package
to get a standarized logger that can be compatible with elastic search.

The way to create a simple logger is by following the next example:

.. code-block:: python

    import logging
    from elasticlogger import Logger

    logger = Logger("test-logger", level=logging.DEBUG)

This will create a logger instance with DEBUG level.

* You can simple log like this:

.. code-block:: python

    logger.debug("test logger message")
    # {"message": "testlogger message", "levelname": "DEBUG", "name": "test-logger"}

* To enable the elasticsearch integration yo need to call the next function

.. code-block:: python

    # setup the elasticsearch endpoint of your cluster and the default index
    logger.enable_elastic(endpoint="https://elastic-cluster.com", index="test-index")

    # you can simply call the function and the data will be take from the envvars
    # ELASTIC_sEARCH_ENDPOINT and ELASTIC_sEARCH_INDEX
    logger.enable_elastic()
