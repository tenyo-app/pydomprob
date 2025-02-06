from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from domprob.announcements.exceptions import AnnouncementException

if TYPE_CHECKING:
    from domprob.announcements.method import (  # pragma: no cover
        BoundAnnouncementMethod,
    )


class ValidatorException(AnnouncementException):
    """Exception raised when a validation error occurs in a validator.

    This exception is used to indicate that validation has failed
    during the execution of a validation chain. It inherits from
    `AnnouncementException` to ensure consistency in exception handling
    across the package.
    """


class BaseValidator(ABC):
    """
    Abstract base class for creating validators in a chain of
    responsibility pattern.

    This class defines a structure for implementing validation logic
    where each validator can perform a specific validation task and
    optionally pass the validation responsibility to the next validator
    in the chain. Subclasses must override the `validate` method to
    provide specific validation logic.

    Args:
        next_ (BaseValidator | None, optional): The next validator in
            the chain. Defaults to `None`, indicating no further
            validation.

    Attributes:
        next_ (BaseValidator | None): Holds the reference to the next
            validator in the chain or `None` if this is the last
            validator.

    Examples:
        >>> from domprob.announcements.validation.base_validator import BaseValidator
        >>> from domprob.announcements.method import AnnouncementMethod
        >>>
        >>> class ExampleValidator(BaseValidator):
        ...     def validate(self, method: BoundAnnouncementMethod) -> None:
        ...         if not method.instrument:
        ...             raise ValueError("Instrument is required")
        ...         print("Validation successful")
        ...         super().validate(method)
        ...
        >>> # Mock setup for example
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class Cls:
        ...     def method(self, instrument: SomeInstrument) -> None:
        ...         pass
        ...
        >>> meth = AnnouncementMethod(Cls.method)
        >>> bound_meth = meth.bind(Cls(), SomeInstrument())
        >>> validator = ExampleValidator()
        >>> validator.validate(bound_meth)
        Validation successful

        >>> # Chaining validators
        >>> validator1 = ExampleValidator()
        >>> validator2 = ExampleValidator(next_=validator1)
        >>> validator2.validate(bound_meth)
        Validation successful
        Validation successful
    """

    def __init__(self, next_: BaseValidator | None = None) -> None:
        self.next_ = next_

    @abstractmethod
    def validate(self, b_meth: BoundAnnouncementMethod) -> None:
        """Validates a `BoundAnnouncementMethod` instance.

        This method performs the validation logic for the current
        validator and delegates to the next validator in the chain if
        one is defined. Subclasses must implement the specific
        validation logic by overriding this method.

        Args:
            b_meth (BoundAnnouncementMethod): Bound method wrapper to
                validate.

        Raises:
            ValidatorException: If the validation fails.
            Exception: If an unexpected error occurs during validation.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.method import AnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, meth: BoundAnnouncementMethod) -> None:
            ...         if not meth.instrument:
            ...             raise ValidatorException("Instrument is required")
            ...         print("Validation successful")
            ...         super().validate(meth)
            ...
            >>> # Mock setup for example
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class Cls:
            ...     def method(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> meth = AnnouncementMethod(Cls.method)
            >>> bound_meth = meth.bind(Cls(), SomeInstrument())
            >>> validator = ExampleValidator()
            >>> validator.validate(bound_meth)
            Validation successful
        """
        if self.next_:
            return self.next_.validate(b_meth)
        return None

    def __repr__(self) -> str:
        """Returns a string representation of the validator.

        This includes the class name and the `next_` validator in the
        chain, making it easier to debug and inspect validator chains.

        Returns:
            str: A string representation of the validator.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, meth: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> validator = ExampleValidator(next_=None)
            >>> repr(validator)
            'ExampleValidator(next_=None)'
            >>> chained_validator = ExampleValidator(next_=validator)
            >>> repr(chained_validator)
            'ExampleValidator(next_=ExampleValidator(next_=None))'
        """
        return f"{self.__class__.__name__}(next_={self.next_!r})"

    def __str__(self) -> str:
        """Returns a human-readable string representation of the
        validator.

        Returns:
            str: The class name of the validator.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, meth):
            ...         pass
            ...
            >>> validator = ExampleValidator()
            >>> str(validator)
            'ExampleValidator'
        """
        return f"{self.__class__.__name__}"
