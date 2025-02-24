from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from domprob.sensors.exc import SensorException

if TYPE_CHECKING:
    from domprob.sensors.meth import (  # pragma: no cover
        BoundSensorMethod,
    )


class ValidatorException(SensorException):
    """Exception raised when a validate error occurs in a validator.

    This exception is used to indicate that validate has failed
    during the execution of a validate chain. It inherits from
    `SensorException` to ensure consistency in exception handling
    across the package.
    """


class BaseValidator(ABC):
    """
    Abstract base class for creating validators in a chain of
    responsibility pattern.

    This class defines a structure for implementing validate logic
    where each validator can perform a specific validate task and
    optionally pass the validate responsibility to the next validator
    in the chain. Subclasses must override the `validate` method to
    provide specific validate logic.

    Args:
        next_ (BaseValidator | None, optional): The next validator in
            the chain. Defaults to `None`, indicating no further
            validate.

    Attributes:
        next_ (BaseValidator | None): Holds the reference to the next
            validator in the chain or `None` if this is the last
            validator.

    Examples:
        >>> from domprob.sensors.validate.base_val import BaseValidator
        >>> from domprob.sensors.meth import SensorMethod
        >>>
        >>> class ExampleValidator(BaseValidator):
        ...     def validate(self, method: BoundSensorMethod) -> None:
        ...         if not method.instrum:
        ...             raise ValueError("Instrument is required")
        ...         print("Validation successful")
        ...         super().validate(method)
        ...
        >>> # Mock setup for example
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class Cls:
        ...     def method(self, instrum: SomeInstrument) -> None:
        ...         pass
        ...
        >>> meth = SensorMethod(Cls.method)
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
    def validate(self, b_meth: BoundSensorMethod) -> None:
        # noinspection PyShadowingNames
        """Validates a `BoundSensorMethod` instance.

        This method performs the validate logic for the current
        validator and delegates to the next validator in the chain if
        one is defined. Subclasses must implement the specific
        validate logic by overriding this method.

        Args:
            b_meth (BoundSensorMethod): Bound method wrapper to
                validate.

        Raises:
            ValidatorException: If the validate fails.
            Exception: If an unexpected error occurs during validate.

        Examples:
            >>> from domprob.sensors.validate.base_val import BaseValidator
            >>> from domprob.sensors.meth import SensorMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, meth: BoundSensorMethod) -> None:
            ...         if not meth.instrum:
            ...             raise ValidatorException("Instrument is required")
            ...         print("Validation successful")
            ...         super().validate(meth)
            ...
            >>> # Mock setup for example
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class Cls:
            ...     def method(self, instrum: SomeInstrument) -> None:
            ...         pass
            ...
            >>> meth = SensorMethod(Cls.method)
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
            >>> from domprob.sensors.validate.base_val import BaseValidator
            >>> from domprob.sensors.meth import BoundSensorMethod
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, meth: BoundSensorMethod) -> None:
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
            >>> from domprob.sensors.validate.base_val import BaseValidator
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, meth):
            ...         pass
            ...
            >>> validator = ExampleValidator()
            >>> str(validator)
            'ExampleValidator'
        """
        return f"{self.__class__.__name__}"
