import pytest

from domprob.announcements.instruments import Instruments
from domprob.announcements.metadata import AnnouncementMetadata
from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.validators import (
    InstrumentParamExistsValidator,
    InstrumentTypeException,
    InstrumentTypeValidator,
    MissingInstrumentException,
)
from domprob.instrument import BaseInstrument


class MockInstrument(BaseInstrument):
    pass


class AnotherInstrument(BaseInstrument):
    pass


@pytest.fixture
def mock_instrument_method():
    """Fixture for creating a mock BoundAnnouncementMethod."""

    def method(instrument: MockInstrument):
        pass

    return BoundAnnouncementMethod(method, MockInstrument())


@pytest.fixture
def mock_no_instrument_method():
    def method(instrument: MockInstrument):
        pass

    return BoundAnnouncementMethod(method)


@pytest.fixture
def mock_none_instrument_method():
    def method(instrument: MockInstrument):
        pass

    return BoundAnnouncementMethod(method, None)


class TestInstrumentParamExistsValidator:

    @pytest.fixture
    def param_exists_validator(self) -> InstrumentParamExistsValidator:
        return InstrumentParamExistsValidator()

    def test_raises_exception_when_instrument_is_none(
        self, param_exists_validator, mock_no_instrument_method
    ):
        # Arrange
        # Act
        with pytest.raises(MissingInstrumentException) as exc_info:
            param_exists_validator.validate(mock_no_instrument_method)
        # Assert
        assert exc_info.value.method == mock_no_instrument_method.method
        assert str(exc_info.value) == (
            f"'instrument' parameter missing in method "
            f"'{mock_no_instrument_method.method.__name__}()'"
        )

    def test_passes_validation_when_instrument_is_present(
        self, param_exists_validator, mock_instrument_method
    ):
        # Arrange
        # Act
        param_exists_validator.validate(mock_instrument_method)
        # Assert
        assert True

    def test_missing_instrument_exception_message(
        self, mock_no_instrument_method
    ):
        # Arrange
        # Act
        exc = MissingInstrumentException(mock_no_instrument_method.method)
        # Assert
        assert str(exc) == (
            f"'instrument' parameter missing in method "
            f"'{mock_no_instrument_method.method.__name__}()'"
        )


class TestInstrumentTypeValidator:
    """Test suite for the InstrumentTypeValidator."""

    @pytest.fixture
    def type_validator(self):
        """Fixture for creating an InstrumentTypeValidator."""
        return InstrumentTypeValidator()

    def test_validate_passes_for_valid_instrument(
        self, type_validator, mock_instrument_method
    ):
        # Arrange
        metadata = AnnouncementMetadata(mock_instrument_method)
        instruments = Instruments(metadata)
        instruments.record(MockInstrument)
        mock_instrument_method._instruments = instruments
        # Act
        type_validator.validate(mock_instrument_method)
        # Assert
        assert True

    def test_validate_raises_for_invalid_instrument(
        self, type_validator, mock_instrument_method
    ):
        # Arrange
        metadata = AnnouncementMetadata(mock_instrument_method)
        instruments = Instruments(metadata)
        instruments.record(AnotherInstrument)
        mock_instrument_method._instruments = instruments
        # Act
        with pytest.raises(InstrumentTypeException) as exc_info:
            type_validator.validate(mock_instrument_method)
        # Assert
        assert (
            str(exc_info.value)
            == f"Method '{mock_instrument_method.method.__name__}()' "
            f"expects 'instrument' to be one of: AnotherInstrument, but got"
            f" '{mock_instrument_method.instrument!r}'"
        )

    def test_validate_raises_for_empty_supported_instruments(
        self, type_validator, mock_instrument_method
    ):
        # Arrange
        # Act
        with pytest.raises(InstrumentTypeException) as exc_info:
            type_validator.validate(mock_instrument_method)
        # Assert
        assert (
            str(exc_info.value)
            == f"Method '{mock_instrument_method.method.__name__}()' "
            f"expects 'instrument' to be one of: , but got "
            f"'{mock_instrument_method.instrument!r}'"
        )

    def test_validate_raises_for_none_instrument(
        self, type_validator, mock_none_instrument_method
    ):
        # Arrange
        metadata = AnnouncementMetadata(mock_none_instrument_method)
        instruments = Instruments(metadata)
        instruments.record(AnotherInstrument)
        mock_none_instrument_method._instruments = instruments
        # Act
        with pytest.raises(InstrumentTypeException) as exc_info:
            type_validator.validate(mock_none_instrument_method)
        # Assert
        exc = exc_info.value
        assert exc.instrument is None
        assert (
            str(exc)
            == f"Method '{mock_none_instrument_method.method.__name__}()' "
            f"expects 'instrument' to be one of: AnotherInstrument, but"
            f" got 'None'"
        )

    def test_validate_with_multiple_valid_instruments(
        self, type_validator, mock_instrument_method
    ):
        # Arrange
        metadata = AnnouncementMetadata(mock_instrument_method)
        instruments = Instruments(metadata)
        instruments.record(MockInstrument)
        instruments.record(AnotherInstrument)
        mock_instrument_method._instruments = instruments
        # Act
        type_validator.validate(mock_instrument_method)
        # Assert
        assert True
