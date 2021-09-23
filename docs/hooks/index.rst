Logger Hooks
============

Logger hooks are functions or callable classes that receive all the logging information that should be logged
by the instance in any of the calls of the debug, info, warning, error, fatal or critical methods.

Hooks can be used to modify logging message or extra data fields before being logged, stream log records
to any other platform or trigger any other feature on certain log data conditions.

- Example:

.. code-block:: python

   def hook_function(context: HookContext) -> NoReturn:
       if 'foo' in context.extra_data:
           del context.extra_data['foo']

   logger.add_hook(hook_function)

- Example 2:

.. code-block:: python

    from elasticlogger import Logger
    from elasticlogger.hooks import HookContext


    class HookClass:
        def __call__(self, context: HookContext) -> NoReturn:
            if 'bar' in context.extra_data:
                context.extra_data['bar'] = context.extra_data['foo']

    logger = Logger('test')
    logger.add_hook(HookClass())


.. toctree::
   :maxdepth: 1
   :caption: Available hooks:

   ./elasticsearch/index
