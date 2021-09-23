"""Custom module errors"""


class InvalidLogLevel(Exception):
    """Error raised when an invalid log level is detected"""


class ContextKeyError(Exception):
    """Error for invalid type of a Context key"""
