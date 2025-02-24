from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from domprob.sensors.validate.base_val import (
    BaseValidator,
    ValidatorException,
)

if TYPE_CHECKING:
    from domprob.sensors.meth import (  # pragma: no cover
        BoundSensorMethod,
    )


class MissingInstrumException(ValidatorException):
    """Exception raised when the `instrument` parameter is missing
    during a call to a method.

    Args:
        method (Callable[..., Any]): The method where the missing
            `instrum` parameter was detected.

    Attributes:
        method (Callable[..., Any]): The method that caused the
            exception.

    Examples:
        >>> from domprob.sensors.validate.vals import MissingInstrumException
        >>> class Example:
        ...     def method(self):
        ...         pass
        ...
        >>> try:
        ...     raise MissingInstrumException(Example().method)
        ... except MissingInstrumException as e:
        ...     print(f"Error: {e}")
        ...
        Error: 'instrum' param missing in Example.method(...)
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
            "'instrum' param missing in Example.method(...)"
        """
        m_name = f"{'.'.join(self.method.__qualname__.split('.')[-2:])}(...)"
        return f"'instrum' param missing in {m_name}"


# pylint: disable=too-few-public-methods
class InstrumentParamExistsValidator(BaseValidator):
    """Validator to check if the `instrum` parameter exists.

    This validator raises a `MissingInstrumException` if the `instrum`
    parameter is `None`.

    Examples:
        >>> from domprob.sensors.validate.vals import InstrumentParamExistsValidator
        >>> from domprob.sensors.meth import SensorMethod
        >>>
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class Example:
        ...     def method(self, instrum: SomeInstrument) -> None:
        ...         pass
        ...
        >>> meth = SensorMethod(Example.method)
        >>> bound_meth = meth.bind(Example())  # type: ignore
        >>>
        >>> validator = InstrumentParamExistsValidator()
        >>> try:
        ...     validator.validate(bound_meth)
        ... except MissingInstrumException as e:
        ...     print(f"Error: {e}")
        ...
        Error: 'instrum' param missing in Example.method(...)
    """

    def validate(self, b_meth: BoundSensorMethod) -> None:
        """Validates the method to ensure the `instrument` parameter
        exists.

        Args:
            b_meth (BoundSensorMethod): Method with bound params to
                validate.

        Raises:
            MissingInstrumentException: If the `instrum` parameter is
                `None`.
        """
        if b_meth.instrum is None:
            raise MissingInstrumException(b_meth.meth)
        return super().validate(b_meth)


class InstrumTypeException(ValidatorException):
    # pylint: disable=line-too-long
    """
    Exception raised when the `instrum` parameter does not match the
    expected type.

    Args:
        b_meth (`BoundSensorMethod`): Bound method that failed
            validate.

    Attributes:
        method (Callable[..., Any]): The method that failed validate.
        instrum (Any): The invalid `instrument` instance.
        supp_instrums (Instruments): The supported instrument types.

    Examples:
        >>> from domprob.sensors.meth import SensorMethod
        >>>
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class Example:
        ...     def method(self, instrum: SomeInstrument) -> None:
        ...         pass
        ...
        >>> meth = SensorMethod(Example.method)
        >>> meth.supp_instrums.record(SomeInstrument, True)
        Instruments(metadata=SensorMetadata(method=<function Example.method at 0x...))
        >>> bound_meth = meth.bind(Example(), 'InvalidInstrument')  # type: ignore
        >>>
        >>> try:
        ...     raise InstrumTypeException(bound_meth)
        ... except InstrumTypeException as e:
        ...     print(f"Error: {e}")
        ...
        Error: Example.method(...) expects 'instrum' param to be one of: [SomeInstrument], but got: 'InvalidInstrument'
    """

    def __init__(self, b_meth: BoundSensorMethod) -> None:
        self.method = b_meth.meth
        self.instrum = b_meth.instrum
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
            f"{m_name} expects 'instrum' param to be one of: "
            f"[{', '.join(instrum_names)}], but got: {self.instrum!r}"
        )


# pylint: disable=too-few-public-methods
class InstrumentTypeValidator(BaseValidator):
    # pylint: disable=line-too-long
    """Validator to check if the `instrum` is of a valid type.

    This validator raises an `InstrumTypeException` if the type of the
    `instrum` parameter is not one of the supported instrument types.

    Examples:
        >>> from domprob.sensors.validate.vals import InstrumentTypeValidator
        >>> from domprob.sensors.meth import SensorMethod
        >>> class MockInstrument:
        ...     pass
        ...
        >>> class Example:
        ...     def method(self, instrum: MockInstrument) -> None:
        ...         pass
        ...
        >>> meth = SensorMethod(Example.method)
        >>> bound_meth = meth.bind(Example(), 'InvalidInstrument')  # type: ignore
        >>>
        >>> validator = InstrumentTypeValidator()
        >>> try:
        ...     validator.validate(bound_meth)
        ... except InstrumTypeException as e:
        ...     print(f"Error: {e}")
        ...
        Error: Example.method(...) expects 'instrum' param to be one of: [], but got: 'InvalidInstrument'
    """

    def validate(self, b_meth: BoundSensorMethod) -> None:
        """Validates the method by checking the type of the
        `instrument` parameter.

        Args:
            b_meth (`BoundSensorMethod`): Method with bound
                params to validate.

        Raises:
            InstrumTypeException: If the `instrum` parameter is not an
                instance of any specified instrument classes.
        """
        for supp_instrum, _ in b_meth.supp_instrums:
            # pylint: disable=unidiomatic-typecheck
            if type(b_meth.instrum) is supp_instrum:
                return super().validate(b_meth)
        raise InstrumTypeException(b_meth)


class NoSupportedInstrumsException(ValidatorException):
    """Exception raised when no supported instruments are defined for a
    method.

    This exception indicates that the method's metadata does not
    include any supported instrument types, which is required for
    proper validate.

    Args:
        method (Callable[..., Any]): The method where the missing
            supported instruments were detected.

    Attributes:
        method (Callable[..., Any]): The method that caused the
            exception.

    Examples:
        >>> from domprob.sensors.validate.vals import NoSupportedInstrumsException
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
        >>> from domprob.sensors.validate.vals import SupportedInstrumentsExistValidator
        >>> from domprob.sensors.meth import SensorMethod
        >>> class Example:
        ...     def method(self, instrument: Any) -> None:
        ...         pass
        ...
        >>> meth = SensorMethod(Example.method)
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

    def validate(self, b_meth: BoundSensorMethod) -> None:
        """Validates the method by checking the type of the
        `instrument` parameter.

        Args:
            b_meth (`BoundSensorMethod`): Method with bound
                params to validate.

        Raises:
            NoSupportedInstrumsException: If the `instrum` parameter is
                not an instance of any valid instrument classes.
        """
        if not b_meth.supp_instrums:
            raise NoSupportedInstrumsException(b_meth.meth)
        return super().validate(b_meth)
