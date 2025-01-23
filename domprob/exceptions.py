"""
exceptions.py
=============

This module defines the public exceptions used in the `pydomprob` library.
It provides a central location to import and expose exceptions related
to announcements, partial binding, validation, and instrument handling.

Imports:
    - `AnnouncementException`: Raised for general issues related to
        announcements.
    - `PartialBindException`: Raised when partial binding of methods
        fails.
    - `ValidatorException`: Base class for validation-related
        exceptions.
    - `InstrumentTypeException`: Raised when an unsupported instrument
        is passed.
    - `MissingInstrumentException`: Raised when a required instrument
        is missing.
    - `NoSupportedInstrumentsException`: Raised when no supported
        instruments are defined.

Attributes:
    __all__ (Sequence[str]): Specifies the public API of this module,
        exposing all exception classes for easy import by other
        modules.

Example Usage:
    >>> from domprob.exceptions import AnnouncementException
    >>>
    >>> def some_method():
    ...     raise AnnouncementException("Something went wrong!")
    ...
"""

from collections.abc import Sequence

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.method import PartialBindException
from domprob.announcements.validation.base_validator import ValidatorException
from domprob.announcements.validation.validators import (
    InstrumentTypeException,
    MissingInstrumentException,
    NoSupportedInstrumentsException,
)

__all__: Sequence[str] = [
    "AnnouncementException",
    "PartialBindException",
    "ValidatorException",
    "InstrumentTypeException",
    "MissingInstrumentException",
    "NoSupportedInstrumentsException",
]
