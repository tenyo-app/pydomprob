from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.base_validator import (
    BaseAnnouncementValidator, ValidatorException)


class MissingInstrumentException(ValidatorException):

    def __init__(self, method) -> None:
        self.method = method
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        return f"'instrument' parameter missing in method '{self.method.__name__}()'"


# pylint: disable=too-few-public-methods
class InstrumentParamExistsValidator(BaseAnnouncementValidator):
    def validate(self, meth: BoundAnnouncementMethod) -> None:
        """Validates the method by checking for the `instrument` parameter.

        Args:
            meth (`InstrumentBoundAnnoMethod`): The method with
                metadata to validate.

        Raises:
            AnnoValidationException: If the `instrument` parameter is
                missing.
        """
        if meth.instrument is None:
            raise MissingInstrumentException(meth.method)
        return super().validate(meth)


class InstrumentTypeException(ValidatorException):

    def __init__(self, method, instrument, *supported_instruments) -> None:
        self.method = method
        self.instrument = instrument
        self.supported_instruments = supported_instruments
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        instruments_str = ', '.join(i.__class__.__name__ for i in
                                    self.supported_instruments)
        return (
            f"Function '{self.method.__name__}()' expects 'instrument' to be "
            f"one of: {instruments_str}, but got '{self.instrument!r}'"
        )


# pylint: disable=too-few-public-methods
class InstrumentTypeValidator(BaseAnnouncementValidator):
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
