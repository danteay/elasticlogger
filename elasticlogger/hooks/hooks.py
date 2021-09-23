"""Definition of a hook.

Logger hooks are functions or callable classes that receive all the logging information that should be logged
by the instance in any of the calls of the debug, info, warning, error, fatal or critical methods.

Example:

    def hook_function(context: HookContext) -> NoReturn:
        if 'foo' in context.extra_data:
            del context.extra_data['foo']

    logger.add_hook(hook_function)

Example2:

    class HookClass:
        def __call__(self, context: HookContext) -> NoReturn:
            if 'bar' in context.extra_data:
                context.extra_data['bar'] = context.extra_data['foo']

    logger.add_hook(HookClass())
"""

from typing import Callable, NoReturn

from elasticlogger.hooks.hook_context import HookContext

Hook = Callable[[HookContext], NoReturn]
