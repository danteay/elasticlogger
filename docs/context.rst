Context Data
============

Context data is used to log some common data across all log outputs to make traceability or correlate outputs of the
application.

Using Logger Context
--------------------

Use Logger context is similar to use the **fields** or **field** methods of the Logger class, the main difference is
that context data is not cleared when the logs are prompted, it keeps alive through all the calls.

To configure some context data we need to call the next functions

.. code-block:: python

    import logging
    from elasticlogger import Logger

    logger = Logger("test-logger", logging.DEBUG)

    # Add single context value
    logger.context.field("context_key", "value")

    # Add multiple context values
    logger.context.fields({
        "context_key_m1": "value",
        "context_key_m2": "value"
    })

Context values will override any current extra value with the same name of a context value, giving priority to any
context data across all logs.