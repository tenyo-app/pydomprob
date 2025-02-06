"""
pydomprob.__init__
==================

This module initialises the `pydomprob` package by exposing the
`announcement` decorator from the `domprob.announcements.decorators`
module. The `announcement` decorator is used to manage and validate
metadata for methods related to announcements.

Attributes:
    __all__ (list): Defines the public API of the module, which
        includes the `announcement` decorator.

Usage:
    >>> from domprob import announcement
    >>>
    >>> class SomeInstrument:
    ...     pass
    ...
    >>> class SomeClass:
    ...     @announcement(SomeInstrument)
    ...     def example_method(self, instrument: SomeInstrument) -> None:
    ...         pass
    ...
"""

from collections.abc import Sequence

from domprob.announcements.decorators import announcement
from domprob.observations.base import BaseObservation

__all__: Sequence[str] = ["announcement", "BaseObservation"]
