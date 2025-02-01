import inspect
from collections import OrderedDict

import pytest

from domprob.announcements.instruments import Instruments
from domprob.announcements.metadata import AnnouncementMetadata
from domprob.announcements.method import BoundAnnouncementMethod, \
    AnnouncementMethod
from domprob.announcements.validation.validators import (
    InstrumentParamExistsValidator,
    InstrumentTypeException,
    InstrumentTypeValidator,
    MissingInstrumentException,
    NoSupportedInstrumentsException,
    SupportedInstrumentsExistValidator,
)


class MockInstrument:
    pass


class AnotherInstrument:
    pass


def _create_b_meth(*args, **kwargs):
    class Cls:
        def method(self, instrument: MockInstrument) -> None:
            pass

    announce_meth = AnnouncementMethod(Cls.method)
    sig = inspect.signature(Cls.method)
    b_params = inspect.BoundArguments(sig, OrderedDict())
    # Bind the arguments correctly
    bound = sig.bind_partial(Cls(), *args, **kwargs)
    # Assign the correct args and kwargs
    b_params.arguments = bound.arguments
    return BoundAnnouncementMethod(announce_meth, b_params)


class TestInstrumentParamExistsValidator:

    @pytest.fixture
    def param_exists_validator(self) -> InstrumentParamExistsValidator:
        return InstrumentParamExistsValidator()

    def test_raises_exception_when_instrument_is_none(
        self, param_exists_validator
    ):
        # Arrange
        b_mock_meth = _create_b_meth()
        # Act
        with pytest.raises(MissingInstrumentException) as exc_info:
            param_exists_validator.validate(b_mock_meth)
        # Assert
        assert exc_info.value.method == b_mock_meth.meth
        assert str(exc_info.value) == (
            "'instrument' param missing in Cls.method(...)"
        )

    def test_passes_validation_when_instrument_is_present(
        self, param_exists_validator
    ):
        # Arrange
        b_mock_meth = _create_b_meth(MockInstrument())
        # Act
        param_exists_validator.validate(b_mock_meth)
        # Assert
        assert True


class TestInstrumentTypeValidator:

    @pytest.fixture
    def type_validator(self):
        return InstrumentTypeValidator()

    def test_validate_passes_for_valid_instrument(
        self, type_validator
    ):
        # Arrange
        b_mock_meth = _create_b_meth(MockInstrument())
        instruments = Instruments(AnnouncementMetadata(b_mock_meth.meth))
        instruments.record(MockInstrument)
        # Act
        type_validator.validate(b_mock_meth)
        # Assert
        assert True

    def test_validate_raises_for_invalid_instrument(
        self, type_validator
    ):
        # Arrange
        b_mock_meth = _create_b_meth(MockInstrument())
        instruments = Instruments(AnnouncementMetadata(b_mock_meth.meth))
        instruments.record(AnotherInstrument)
        # Act
        with pytest.raises(InstrumentTypeException) as exc_info:
            type_validator.validate(b_mock_meth)
        # Assert
        assert (
            str(exc_info.value)
            == f"Cls.method(...) expects 'instrument' param to be "
            f"one of: [AnotherInstrument], but got: "
            f"{b_mock_meth.instrument!r}"
        )

    def test_validate_raises_for_empty_supported_instruments(
        self, type_validator
    ):
        # Arrange
        b_mock_meth = _create_b_meth(MockInstrument())
        # Act
        with pytest.raises(InstrumentTypeException) as exc_info:
            type_validator.validate(b_mock_meth)
        # Assert
        assert (
            str(exc_info.value)
            == f"Cls.method(...) expects 'instrument' param to be "
            f"one of: [], but got: {b_mock_meth.instrument!r}"
        )

    def test_validate_raises_for_none_instrument(
        self, type_validator
    ):
        # Arrange
        b_mock_meth = _create_b_meth(None)
        instruments = Instruments(AnnouncementMetadata(b_mock_meth.meth))
        instruments.record(AnotherInstrument)
        # Act
        with pytest.raises(InstrumentTypeException) as exc_info:
            type_validator.validate(b_mock_meth)
        # Assert
        exc = exc_info.value
        assert exc.instrument is None
        assert (
            str(exc) == f"Cls.method(...) expects 'instrument' param to be "
            f"one of: [AnotherInstrument], but got: None"
        )

    def test_validate_with_multiple_valid_instruments(
        self, type_validator
    ):
        # Arrange
        b_mock_meth = _create_b_meth(MockInstrument())
        instruments = Instruments(AnnouncementMetadata(b_mock_meth.meth))
        instruments.record(MockInstrument)
        instruments.record(AnotherInstrument)
        # Act
        type_validator.validate(b_mock_meth)
        # Assert
        assert True


class TestSupportedInstrumentsExistValidator:
    @pytest.fixture
    def supported_instruments_validator(
        self,
    ) -> SupportedInstrumentsExistValidator:
        return SupportedInstrumentsExistValidator()

    def test_validate_passes_with_supported_instruments(
        self, supported_instruments_validator
    ):
        # Arrange
        b_mock_meth = _create_b_meth(MockInstrument())
        instruments = Instruments(AnnouncementMetadata(b_mock_meth.meth))
        instruments.record(MockInstrument)
        # Act
        supported_instruments_validator.validate(b_mock_meth)
        # Assert
        assert True

    def test_validate_raises_no_supported_instruments_exception(
        self, supported_instruments_validator
    ):
        # Arrange
        b_mock_meth = _create_b_meth(None)
        # Act
        with pytest.raises(NoSupportedInstrumentsException) as exc_info:
            supported_instruments_validator.validate(
                b_mock_meth
            )
        # Assert
        assert exc_info.value.method == b_mock_meth.meth
        assert (
            str(exc_info.value)
            == f"Cls.method(...) has no supported instrument types defined"
        )

    def test_no_supported_instruments_exception_message(self):
        # Arrange
        b_mock_meth = _create_b_meth()
        exc = NoSupportedInstrumentsException(b_mock_meth.meth)
        # Act & Assert
        assert (
            str(exc)
            == f"Cls.method(...) has no supported instrument types defined"
        )
