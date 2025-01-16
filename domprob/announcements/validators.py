from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TypeAlias

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.instruments import Instruments
from domprob.announcements.method import InstrumentBoundAnnoMethod
from domprob.instrument import BaseInstrument

_Validator: TypeAlias = "ABCAnnouncementValidator"
_ValidatorExc: TypeAlias = "AnnoValidatorException"


class AnnoValidatorException(AnnouncementException):
    """Exception raised for validation errors in the announcements
    framework.

    This exception handles errors related to the validation of methods
    and their metadata, including issues with instruments or the
    validation chain.
    """

    @classmethod
    def instrument_type(
        cls,
        method: Callable[[BaseInstrument], None],
        instrument: BaseInstrument,
        *supported: Instruments,
    ) -> _ValidatorExc:
        """Creates an exception for an invalid instrument type.

        Args:
            meth (`InstrumentBoundAnnoMethod`): The method being
                validated, where the instrument type mismatch occurred.

        Returns:
            AnnoValidationException: The exception instance with a
                descriptive error message.

        Examples:
            >>> from domprob import announcement
            >>> from domprob.instrument import BaseInstrument
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcement(BaseInstrument)
            ...     def bar(self, instrument: BaseInstrument):
            ...         pass
            ...
            >>> # Create instrument bound method instance
            >>> args = (Foo(), "invalid_instrument")
            >>> method = InstrumentBoundAnnoMethod(Foo.bar, *args)
            >>>
            >>> raise AnnoValidationException.instrument_type(method)
            Traceback (most recent call last):
            AnnoValidationException: Function 'bar' expects
            'instrument' to be one of: BaseInstrument, but got
            'invalid_instrument'
        """
        return cls(
            f"Function '{method.__name__}()' expects 'instrument' to be one"
            f" of: {', '.join((i__name__ for i in supported))}, but got "
            f"'{instrument!r}'"
        )

    @classmethod
    def missing_instrument(
        cls,
        method: Callable[[BaseInstrument], None],
    ) -> _ValidatorExc:
        """Creates an exception for a missing `instrument` parameter.

        Args:
            meth (`InstrumentBoundAnnoMethod`): The method being
                validated, where the `instrument` parameter was
                missing.

        Returns:
            AnnoValidationException: The exception instance with a
            descriptive error message.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument: BaseInstrument):
            ...         pass
            ...
            >>> # Create instrument bound method instance
            >>> args = (Foo(), "invalid_instrument")
            >>> method = InstrumentBoundAnnoMethod(Foo.bar, *args)
            >>>
            >>> raise AnnoValidationException.missing_instrument(method)
            Traceback (most recent call last):
            AnnoValidationException: 'instrument' parameter missing in
            function 'bar'
        """
        return cls(
            f"'instrument' parameter missing in method '{method.__name__}()'"
        )


class ABCAnnouncementValidator(ABC):
    """This abstract base class represents a single validator in a
    chain of responsibility. Each validator can process a method's
    metadata and pass it to the next validator in the chain.

    Args:
        next_validator (TValidator | None): The next validator in
            the chain. Defaults to `None` if it is the last in the
            chain.
    """

    def __init__(self, next_validator: _Validator | None = None) -> None:
        self.next = next_validator

    @abstractmethod
    def validate(self, meth: InstrumentBoundAnnoMethod) -> None:
        # noinspection PyShadowingNames
        """Validates a method's metadata. Subclasses must implement
        this method to provide custom validation logic.

        Args:
            meth (InstrumentBoundAnnoMethod): The method with metadata
                to validate.

        Raises:
            AnnoValidationException: If validation fails.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         print(f\"Executing with {instrument!r}\")
            ...
            >>> # Create an InstrumentBoundAnnoMethod instance
            >>> args = (Foo(), BaseInstrument())
            >>> bound_method = InstrumentBoundAnnoMethod(Foo.bar, *args)
            >>>
            >>> # Define a validator
            >>> class CustomValidator(ABCAnnouncementValidator):
            ...     def validate(self, meth):
            ...         raise AnnoValidationException("Validation exception")
            ...
            >>> validator = CustomValidator()
            >>>
            >>> validator.validate(bound_method)
            Traceback (most recent call last):
            AnnoValidationException: Validation exception
        """
        if self.next:
            return self.next.validate(meth)
        return None

    def __repr__(self) -> str:
        """Returns a string representation of the validator, including
        the next validator in the chain if it exists.

        Returns:
            str: The string representation.

        Examples:
            >>> # Define a validator
            >>> class CustomValidator(ABCAnnouncementValidator):
            ...     def validate(self, meth):
            ...         raise AnnoValidationException("Validation exception")
            ...
            >>> validator = CustomValidator()
            >>> repr(validator)
            "CustomValidator(next_validator=None)"
        """
        return f"{self.__class__.__name__}(next_validator={self.next})"


# pylint: disable=too-few-public-methods
class InstrumentParamExistsValidator(ABCAnnouncementValidator):
    """Validator to ensure the `instrument` parameter is present.

    This validator checks whether the `instrument` parameter is bound
    to the decorated method during runtime. If the parameter is missing,
    an exception is raised.

    Examples:
        >>> # Define a class with a decorated method
        >>> class Foo:
        ...     @announcements(BaseInstrument)
        ...     def bar(self, instrument):
        ...         pass
        ...
        >>> # Create an InstrumentBoundAnnoMethod instance
        >>> args = (Foo(), )  # missing `instrument` arg
        >>> bound_method = InstrumentBoundAnnoMethod(Foo.bar, *args)
        >>>
        >>> # Initialise the validator
        >>> validator = InstrumentParamExistsValidator()
        >>>
        >>> validator.validate(bound_method)
        Traceback (most recent call last):
        AnnoValidationException: 'instrument' parameter missing in function 'bar'
    """

    def validate(self, meth: InstrumentBoundAnnoMethod) -> None:
        """Validates the method by checking for the `instrument` parameter.

        Args:
            meth (`InstrumentBoundAnnoMethod`): The method with
                metadata to validate.

        Raises:
            AnnoValidationException: If the `instrument` parameter is
                missing.
        """
        if meth.instrument is None:
            raise AnnoValidatorException.missing_instrument(meth.method)
        return super().validate(meth)


# pylint: disable=too-few-public-methods
class InstrumentTypeValidator(ABCAnnouncementValidator):
    """Validator to ensure the `instrument` parameter is of a valid
    type.

    This validator checks whether the `instrument` parameter bound to
    the decorated method is an instance of any of the valid instrument
    classes specified in the method's metadata. If the `instrument`
    parameter's type is invalid, an exception is raised.

    Examples:
        >>> # Define a class with a decorated method
        >>> class Foo:
        ...     @announcements(BaseInstrument)
        ...     def bar(self, instrument):
        ...         pass
        ...
        >>> # Create an InstrumentBoundAnnoMethod instance
        >>> args = (Foo(), BaseInstrument())  # Valid instrument
        >>> bound_method = InstrumentBoundAnnoMethod(Foo.bar, *args)
        >>>
        >>> # Initialise the validator
        >>> validator = InstrumentTypeValidator()
        >>> validator.validate(bound_method)  # No exception raised
        >>>
        >>> # Create an InstrumentBoundAnnoMethod instance
        >>> args = (Foo(), "invalid_instrument")  # Invalid instrument
        >>> invalid_method = InstrumentBoundAnnoMethod(Foo.bar, *args)
        >>>
        >>> # Validate the invalid method
        >>> validator.validate(invalid_method)
        Traceback (most recent call last):
        AnnoValidationException: Function 'bar' expects 'instrument' to be one of:
        BaseInstrument, but got 'str'
    """

    def validate(self, meth: InstrumentBoundAnnoMethod) -> None:
        """Validates the method by checking the type of the
        `instrument` parameter.

        Args:
            meth (`InstrumentBoundAnnoMethod`): The method with
                metadata to validate.

        Raises:
            AnnoValidationException: If the `instrument` parameter is
                not an instance of any valid instrument classes.
        """
        if not any(isinstance(meth.instrument, i) for i in meth.instruments):
            raise AnnoValidatorException.instrument_type(
                meth.method, meth.instrument, meth.instruments
            )
        return super().validate(meth)
