"""
This module defines custom exceptions for the `@announcement`
functionality in the `domprob` framework. These exceptions provide
meaningful error messages and are organised hierarchically for better
error handling and debugging.

**Key Classes**

- `AnnouncementException`:
  The base exception for all errors related to the `@announcement`
  functionality. It serves as a parent class for more specific
  exceptions in the framework.

**Usage**

These exceptions are designed to be used internally by the `domprob`
framework. Developers can raise these exceptions when validating
inputs, executing decorated methods, or handling invalid operations
within the announcement mechanism.

**Examples**

>>> from domprob.announcements.exceptions import AnnouncementException
>>>
>>> # Define a specific exception inheriting from AnnouncementException
>>> class ValidationError(AnnouncementException):
...     pass
...
>>> # Raise the custom exception
>>> def raise_validation_error():
...     raise ValidationError("Validation failed for input data")
...
>>> try:
...     raise_validation_error()
... except ValidationError as e:
...     print(f"Error: {e}")
Error: Validation failed for input data
"""

from domprob.base_exception import DomprobException


class AnnouncementException(DomprobException):
    """Base exception class for errors related to the `@announcement`
    functionality.

    This serves as a parent class for all exceptions raised within
    the announcements framework.
    """
