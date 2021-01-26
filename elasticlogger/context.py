"""Logger context data store"""

from contextlib import ContextDecorator


class Context(ContextDecorator):
    """
    Context manager for global and persistent logger data
    """

    def __init__(self):
        self.data = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def field(self, name: str, value):
        """
        Add single field to context data. Context data will be logged in all logs and never is auto cleaned
        :param name: New key name for the field
        :param value: Value of the field (if it's an object needs to be json serializable)
        :return: Self instance
        """

        self.data.update({name: value})

    def fields(self, fields: dict):
        """
        Add fields to context data. Context data will be logged in all logs and never is auto cleaned
        :param fields: (dict) Extra fields to add in the json log
        :return: Self instance
        """

        self.data.update(fields)

    def clear(self):
        """
        Delete all previous context data
        :return: Self instance
        """

        self.data = {}
