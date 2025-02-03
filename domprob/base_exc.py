"""
base_exception.py
=================

This module defines the base exception class for the `pydomprob`
package. All custom exceptions in the package should inherit from
`DomprobException`.

Purpose:
--------
The `DomprobException` serves as a root exception to enable structured
and consistent error handling throughout the package.

Usage:
------
Subclass `DomprobException` to define more specific exceptions as
needed.
"""


class DomprobException(Exception):
    """
    The base exception class for the `domprob` package.

    All custom exceptions within the package should inherit from
    `DomprobException` to enable centralised error handling.

    This class does not define additional behaviour but provides a
    consistent base for more specific exceptions.
    """
