from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from domprob.announcements.validation.base_validator import (
    BaseValidator,
    ValidatorException,
)

if TYPE_CHECKING:
    from domprob.announcements.method import (  # pragma: no cover
        BoundAnnouncementMethod,
    )


class MissingInstrumException(ValidatorException):
    """Exception raised when the `instrument` parameter is missing during
    a call to a method.

    Args:
        method (Callable[..., Any]): The method where the missing
            `instrument` parameter was detected.

    Attributes:
        method (Callable[..., Any]): The method that caused the
            exception.

    Examples:
        >>> from domprob.announcements.validation.validators import MissingInstrumException
        >>> class Example:
        ...     def method(self):
        ...         pass
        ...
        >>> try:
        ...     raise MissingInstrumException(Example().method)
        ... except MissingInstrumException as e:
        ...     print(f"Error: {e}")
        ...
        Error: 'instrument' param missing in Example.method(...)
    """

    def __init__(self, method: Callable[..., Any]) -> None:
        self.method = method
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Constructs a detailed error message.

        Returns:
            str: Error message indicating the missing `instrument`
                parameter.

        Examples:
            >>> class Example:
            ...     def method(self):
            ...         pass
            ...
            >>> exc = MissingInstrumException(Example().method)
            >>> exc.msg
            "'instrument' param missing in Example.method(...)"
        """
        m_name = f"{'.'.join(self.method.__qualname__.split('.')[-2:])}(...)"
        return f"'instrument' param missing in {m_name}"


# pylint: disable=too-few-public-methods
class InstrumentParamExistsValidator(BaseValidator):
    """Validator to check if the `instrument` parameter exists.

    This validator raises a `MissingInstrumentException` if the
    `instrument` parameter is `None`.

    Examples:
        >>> from domprob.announcements.validation.validators import InstrumentParamExistsValidator
        >>> from domprob.announcements.method import AnnouncementMethod
        >>>
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class Example:
        ...     def method(self, instrument: SomeInstrument) -> None:
        ...         pass
        ...
        >>> meth = AnnouncementMethod(Example.method)
        >>> bound_meth = meth.bind(Example())
        >>>
        >>> validator = InstrumentParamExistsValidator()
        >>> try:
        ...     validator.validate(bound_meth)
        ... except MissingInstrumException as e:
        ...     print(f"Error: {e}")
        ...
        Error: 'instrument' param missing in Example.method(...)
    """

    def validate(self, b_meth: BoundAnnouncementMethod) -> None:
        """Validates the method to ensure the `instrument` parameter
        exists.

        Args:
            b_meth (BoundAnnouncementMethod): Method with bound
                params to validate.

        Raises:
            MissingInstrumentException: If the `instrument` parameter
                is `None`.
        """
        if b_meth.instrument is None:
            raise MissingInstrumException(b_meth.meth)
        return super().validate(b_meth)


class InstrumTypeException(ValidatorException):
    # pylint: disable=line-too-long
    """
    Exception raised when the `instrument` parameter does not match the
    expected type.

    Args:
        b_meth (`BoundAnnouncementMethod`): Bound method that failed
            validation.

    Attributes:
        method (Callable[..., Any]): The method that failed validation.
        instrument (Any): The invalid `instrument` instance.
        supp_instrums (Instruments): The supported instrument types.

    Examples:
        >>> from domprob.announcements.method import AnnouncementMethod
        >>>
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class Example:
        ...     def method(self, instrument: SomeInstrument) -> None:
        ...         pass
        ...
        >>> meth = AnnouncementMethod(Example.method)
        >>> meth.supp_instrums.record(SomeInstrument, True)
        Instruments(metadata=AnnouncementMetadata(method=<function Example.method at 0x...))
        >>> bound_meth = meth.bind(Example(), 'InvalidInstrument')  # type: ignore
        >>>
        >>> try:
        ...     raise InstrumTypeException(bound_meth)
        ... except InstrumTypeException as e:
        ...     print(f"Error: {e}")
        ...
        Error: Example.method(...) expects 'instrument' param to be one of: [SomeInstrument], but got: 'InvalidInstrument'
    """

    def __init__(self, b_meth: BoundAnnouncementMethod) -> None:
        self.method = b_meth.meth
        self.instrument = b_meth.instrument
        self.supp_instrums = b_meth.supp_instrums
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Constructs a detailed error message.

        Returns:
            str: Error message describing the invalid `instrument`.
        """
        instrum_names = (i.__name__ for i, _ in self.supp_instrums)
        m_name = f"{'.'.join(self.method.__qualname__.split('.')[-2:])}(...)"
        return (
            f"{m_name} expects 'instrument' param to be one of: "
            f"[{', '.join(instrum_names)}], but got: {self.instrument!r}"
        )


# pylint: disable=too-few-public-methods
class InstrumentTypeValidator(BaseValidator):
    # pylint: disable=line-too-long
    """Validator to check if the `instrument` is of a valid type.

    This validator raises an `InstrumentTypeException` if the type of
    the `instrument` parameter is not one of the supported instrument
    types.

    Examples:
        >>> from domprob.announcements.validation.validators import InstrumentTypeValidator
        >>> from domprob.announcements.method import AnnouncementMethod
        >>> class MockInstrument:
        ...     pass
        ...
        >>> class Example:
        ...     def method(self, instrument: MockInstrument) -> None:
        ...         pass
        ...
        >>> meth = AnnouncementMethod(Example.method)
        >>> bound_meth = meth.bind(Example(), 'InvalidInstrument')  # type: ignore
        >>>
        >>> validator = InstrumentTypeValidator()
        >>> try:
        ...     validator.validate(bound_meth)
        ... except InstrumTypeException as e:
        ...     print(f"Error: {e}")
        ...
        Error: Example.method(...) expects 'instrument' param to be one of: [], but got: 'InvalidInstrument'
    """

    def validate(self, b_meth: BoundAnnouncementMethod) -> None:
        """Validates the method by checking the type of the
        `instrument` parameter.

        Args:
            b_meth (`InstrumentBoundAnnoMethod`): Method with bound
                params to validate.

        Raises:
            AnnoValidationException: If the `instrument` parameter is
                not an instance of any valid instrument classes.
        """
        for supp_instrum, _ in b_meth.supp_instrums:
            # pylint: disable=unidiomatic-typecheck
            if type(b_meth.instrument) is supp_instrum:
                return super().validate(b_meth)
        raise InstrumTypeException(b_meth)


class NoSupportedInstrumsException(ValidatorException):
    """Exception raised when no supported instruments are defined for a
    method.

    This exception indicates that the method's metadata does not
    include any supported instrument types, which is required for
    proper validation.

    Args:
        method (Callable[..., Any]): The method where the missing
            supported instruments were detected.

    Attributes:
        method (Callable[..., Any]): The method that caused the
            exception.

    Examples:
        >>> from domprob.announcements.validation.validators import NoSupportedInstrumsException
        >>> class Example:
        ...     def method(self):
        ...         pass
        ...
        >>> try:
        ...     raise NoSupportedInstrumsException(Example().method)
        ... except NoSupportedInstrumsException as e:
        ...     print(f"Error: {e}")
        ...
        Error: Example.method(...) has no supported instrument types defined
    """

    def __init__(self, method: Callable[..., Any]) -> None:
        self.method = method
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """
        Constructs a detailed error message.

        Returns:
            str: Error message indicating that no supported instrument
                types are defined for the method.

        Examples:
            >>> class Example:
            ...     def method(self):
            ...         pass
            ...
            >>> exc = NoSupportedInstrumsException(Example().method)
            >>> exc.msg
            'Example.method(...) has no supported instrument types defined'
        """
        m_name = f"{'.'.join(self.method.__qualname__.split('.')[-2:])}(...)"
        return f"{m_name} has no supported instrument types defined"


# pylint: disable=too-few-public-methods
class SupportedInstrumentsExistValidator(BaseValidator):
    # pylint: disable=line-too-long
    """Validator to ensure that at least one supported instrument is
    defined.

    This validator raises a `NoSupportedInstrumentsException` if the
    method's metadata does not include any supported instrument types.

    Examples:
        >>> from domprob.announcements.validation.validators import SupportedInstrumentsExistValidator
        >>> from domprob.announcements.method import AnnouncementMethod
        >>> class Example:
        ...     def method(self, instrument: Any) -> None:
        ...         pass
        ...
        >>> meth = AnnouncementMethod(Example.method)
        >>> bound_meth = meth.bind(Example())
        >>>
        >>> validator = SupportedInstrumentsExistValidator()
        >>> try:
        ...     validator.validate(bound_meth)
        ... except NoSupportedInstrumsException as e:
        ...     print(f"Error: {e}")
        ...
        Error: Example.method(...) has no supported instrument types defined
    """

    def validate(self, b_meth: BoundAnnouncementMethod) -> None:
        """Validates the method by checking the type of the
        `instrument` parameter.

        Args:
            b_meth (`BoundAnnouncementMethod`): Method with bound
                params to validate.

        Raises:
            AnnoValidationException: If the `instrument` parameter is
                not an instance of any valid instrument classes.
        """
        if not b_meth.supp_instrums:
            raise NoSupportedInstrumsException(b_meth.meth)
        return super().validate(b_meth)
