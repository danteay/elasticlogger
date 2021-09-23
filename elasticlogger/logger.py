"""Logger implementation"""

from typing import AnyStr, List, NoReturn, Optional, Set, Tuple, Union

from elasticlogger import utils
from elasticlogger.hooks import Hook, HookContext
from elasticlogger.types import LinkedList

from .base_logger import BaseLogger


class Logger(BaseLogger):
    """This is the main API class to interact with the JSON logs. Has the needed methods to log information as
    DEBUG, INFO, WARNING and ERROR levels with specific features like adding errors with tracing data,
    communicate events with with Sentry monitoring spaces and the core of this integration, stream your logs
    as Elasticsearch documents in a specific index.

    :param name: Logger name
    :param level: Logger level (Def: DEBUG)
    :param fmt: Log format fields (Def: %(asctime) %(levelname) %(name) %(message))
    :param hooks: List of hook functions to call before logging information
    """

    def __init__(
        self,
        name: AnyStr,
        level: Optional[int] = None,
        fmt: Optional[AnyStr] = None,
        hooks: Optional[Union[Tuple[Hook, ...], Set[Hook], List[Hook]]] = None
    ):
        super().__init__(name, level, fmt)
        self.__hooks = self.__setup_hooks(hooks)

    def add_hook(self, hook: Hook) -> NoReturn:
        """Add new hooks to the logger.

        :param hook: Hook function
        """

        self.__hooks.add(hook)

    def clear_hooks(self) -> NoReturn:
        """Delete all registered hooks of the logger."""
        self.__hooks = LinkedList()

    def log(self, level: int, message: AnyStr, *args, **kwargs) -> NoReturn:
        """Dynamically log data to a specific level.

        :param level: Level of the log message
        :param message: Message to be logged
        """

        log_method = utils.get_logging_method(level, self.logger)
        context = self.__apply_hooks(self.__get_hook_context(level, message))

        kwargs['extra'] = context.extra_data
        message = context.message

        log_method(message, *args, **kwargs)

    def __get_hook_context(self, level: int, message: AnyStr) -> HookContext:
        """Build a context object to pass over all hooks.

        :param level: Current level for the log record
        :param message: Current log record message

        :return HookContext: Collected context information
        """

        return HookContext(
            level=level,
            logger_level=self.level,
            logger_name=self.name,
            message=message,
            extra_data=self._get_extra_data()
        )

    def __apply_hooks(self, context: HookContext) -> HookContext:
        """Apply all registered hooks to extra data and messages.

        :param context: Hook context with all record log information
        """

        for hook in self.__hooks:
            try:
                hook(context)
            except Exception as error:
                self.logger.error('error applying hook %s', hook.__name__, extra=utils.get_error_info(error))

        return context

    @staticmethod
    def __setup_hooks(hooks: Union[Tuple[Hook, ...], Set[Hook], List[Hook]]) -> LinkedList[Hook]:
        """Create a linked list of hooks to be applied before logging information.

        :param hooks: List of hooks to be configured

        :return LinkedList[Hook]: Linked List of hooks
        """

        if hooks is None:
            return LinkedList()

        return LinkedList(hooks)
