class DomprobException(Exception):
    """
    The base exception class for the `domprob` package.

    All custom exceptions within the package should inherit from
    `DomprobException` to enable centralised error handling.

    This class does not define additional behaviour but provides a
    consistent base for more specific exceptions.
    """
