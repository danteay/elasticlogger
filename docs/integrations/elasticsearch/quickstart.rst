Quick Start with Elasticsearch integration
==========================================

Introduction
------------

Elasticlogger has a native implementation of the Elasticsearch driver to stream all your cluster
in a simply and effective way.

To start using this integration is as easy that you just need to call one method:

.. code-block:: python

    from elasticlogger import Logger

    logger = Logger()
    logger.enable_elastic()

This will enable the elastic search integration by searching configs on the env vars `ELASTICSEARCH_URL`
and `ELASTICSEARCH_INDEX`.

Document keys
-------------

Whe you configure the elastic search integration you need to consider the keys that your objects will
contain.

For local logging the keys that are prompted are compliant with the standard key words of the python logger:

* asctime
* name
* levelname
* message

For that reason this keys are treat as reserved keywords and are omitted at the display time.

When Logger stream the logs to Elasticsearch some keywords was changed to be more complaint with Elasticsearch
naming. This is how the keys are converted and streamed to the cluster.

* asctime => @timestamp
* message => @message
* levelname => level

Reserved log key names
----------------------

* asctime
* name
* levelname
* message
* @timestamp
* @message
* level

