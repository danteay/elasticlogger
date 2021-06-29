"""Logger context data store"""

from typing import Dict, Any, AnyStr
from contextlib import ContextDecorator

from .errors import ContextKeyError


class Context(ContextDecorator):
    """Context manager for global and persistent logger data."""

    _data: Dict[AnyStr, Any]

    def __init__(self):
        self._data = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def data(self):
        """Return stored data fo the context."""
        return self._data

    def field(self, name: AnyStr, value: Any):
        """Add single field to context data. Context data will be logged in all logs and never is auto cleaned

        :param name: New key name for the field
        :param value: Value of the field (if it's an object needs to be json serializable)
        :return Context: Self instance
        :raises ContextKeyError: When the given context key is not a str
        """

        if not isinstance(name, str):
            raise ContextKeyError(f"Invalid context value key, expected 'str' got '{name.__class__.__name__}'")

        self._data.update({name: value})

    def fields(self, fields: dict):
        """Add fields to context data. Context data will be logged in all logs and never is auto cleaned

        :param fields: (dict) Extra fields to add in the json log
        :return Context: Self instance
        """

        self._data.update(fields)

    def clear(self):
        """Delete all previous context data"""

        self._data = {}
