"""Hook context that keeps data to be modified."""

from typing import Any, AnyStr, Dict


class HookContext:
    """Context information for hook execution.

    :type level: int
    :param level: Current log record level

    :type logger_level: int
    :param logger_level: Global logger level

    :type logger_name: str
    :param logger_name: Global logger name

    :type message: str
    :param message: Current log record message

    :type extra_data: dict
    :param extra_data: Current log record extra data
    """

    def __init__(
        self, level: int, logger_level: int, logger_name: AnyStr, message: AnyStr, extra_data: Dict[AnyStr, Any]
    ):
        self.__level = level
        self.__logger_level = logger_level
        self.__logger_name = logger_name
        self.message = message
        self.extra_data = extra_data

    @property
    def level(self) -> int:
        """Getter for level property."""
        return self.__level

    @property
    def logger_level(self) -> int:
        """Global logger level."""
        return self.__logger_level

    @property
    def logger_name(self) -> AnyStr:
        """Global logger name."""
        return self.__logger_name
