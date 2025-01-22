from typing import Any, Callable

from domprob.announcements.instruments import Instruments
from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.base_validator import (
    BaseValidator,
    ValidatorException,
)


class MissingInstrumentException(ValidatorException):

    def __init__(self, method: Callable[..., Any]) -> None:
        self.method = method
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        m_name = f"{'.'.join(self.method.__qualname__.split('.')[-2:])}(...)"
        return f"'instrument' param missing in '{m_name}'"


# pylint: disable=too-few-public-methods
class InstrumentParamExistsValidator(BaseValidator):
    def validate(self, meth: BoundAnnouncementMethod) -> None:
        if meth.instrument is None:
            raise MissingInstrumentException(meth.method)
        return super().validate(meth)


class InstrumentTypeException(ValidatorException):

    def __init__(
        self,
        method: Callable[..., Any],
        instrument: Any,
        supported_instruments: Instruments,
    ) -> None:
        self.method = method
        self.instrument = instrument
        self.supported_instruments = supported_instruments
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        instrument_names = (i.__name__ for i in self.supported_instruments)
        m_name = f"{'.'.join(self.method.__qualname__.split('.')[-2:])}(...)"
        return (
            f"{m_name} expects 'instrument' param to be one of: "
            f"[{', '.join(instrument_names)}], but got: {self.instrument!r}"
        )


# pylint: disable=too-few-public-methods
class InstrumentTypeValidator(BaseValidator):
    def validate(self, meth: BoundAnnouncementMethod) -> None:
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
            raise InstrumentTypeException(
                meth.method, meth.instrument, meth.instruments
            )
        return super().validate(meth)


class NoSupportedInstrumentsException(ValidatorException):

    def __init__(self, method: Callable[..., Any]) -> None:
        self.method = method
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        m_name = f"{'.'.join(self.method.__qualname__.split('.')[-2:])}(...)"
        return f"'{m_name}' has no supported instrument types defined"


# pylint: disable=too-few-public-methods
class SupportedInstrumentsExistValidator(BaseValidator):
    def validate(self, meth: BoundAnnouncementMethod) -> None:
        """Validates the method by checking the type of the
        `instrument` parameter.

        Args:
            meth (`InstrumentBoundAnnoMethod`): The method with
                metadata to validate.

        Raises:
            AnnoValidationException: If the `instrument` parameter is
                not an instance of any valid instrument classes.
        """
        if not meth.instruments:
            raise NoSupportedInstrumentsException(meth.method)
        return super().validate(meth)
