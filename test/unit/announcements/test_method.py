from unittest.mock import MagicMock

import pytest

from domprob.announcements.instruments import Instruments
from domprob.announcements.metadata import AnnouncementMetadata
from domprob.announcements.method import (
    AnnouncementMethod,
    BoundAnnouncementMethod,
    PartialBindException,
)


class MockInstrument:
    pass


@pytest.fixture
def mock_method():
    class Cls:
        def method(self, instrument):
            pass

    return Cls.method


@pytest.fixture
def mock_metadata(mock_method):
    return AnnouncementMetadata(mock_method)


@pytest.fixture
def mock_instruments(mock_metadata):
    return Instruments(mock_metadata)


class TestAnnouncementMethod:
    def test_initialisation(self, mock_method, mock_instruments):
        # Arrange
        # Act
        announcement_method = AnnouncementMethod(mock_method)
        # Assert
        assert announcement_method.method == mock_method
        assert announcement_method.instruments == mock_instruments

    def test_signature_property(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        # Act
        signature = announcement_method.signature
        # Assert
        assert str(signature) == "(self, instrument)"

    def test_repr(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        # Act
        meth_repr = repr(announcement_method)
        # Assert
        assert meth_repr == f"AnnouncementMethod(method={mock_method!r})"

    def test_bind(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        mock_instrument = MockInstrument()
        # Act
        bound_method = announcement_method.bind(mock_instrument)
        # Assert
        assert isinstance(bound_method, BoundAnnouncementMethod)
        assert bound_method.params.args == (mock_instrument,)
        assert bound_method.params.kwargs == {}


class TestPartialBindException:
    def test_general_exception(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        exception = TypeError("Some binding error")
        # Act
        result = PartialBindException.general(announcement_method, exception)
        # Assert
        assert isinstance(result, PartialBindException)
        assert "Failed to bind parameters" in str(result)

    def test_missing_param_exception(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        # Act
        result = PartialBindException.missing_param(
            "instrument", announcement_method
        )
        # Assert
        assert isinstance(result, PartialBindException)
        assert "Parameter 'instrument' missing" in str(result)


class TestBoundAnnouncementMethod:
    def test_initialisation(self, mock_method):
        # Arrange
        mock_instrument = MockInstrument()
        # Act
        bound_method = BoundAnnouncementMethod(mock_method, mock_instrument)
        # Assert
        assert bound_method.params.args == (mock_instrument,)
        assert bound_method.params.kwargs == {}

    def test_instrument_property(self, mock_method):
        # Arrange
        bound_method = BoundAnnouncementMethod(
            mock_method, instrument=MockInstrument()
        )
        # Act + Assert
        assert bound_method.instrument is not None
        assert isinstance(bound_method.instrument, MockInstrument)

    def test_bind_partial_success(self, mock_method):
        # Arrange
        bound_method = BoundAnnouncementMethod(mock_method)
        mock_instrument = MockInstrument()
        # Act
        bound_arguments = bound_method.bind_partial(mock_instrument)
        # Assert
        assert bound_arguments.args == (mock_instrument,)
        assert bound_arguments.kwargs == {}

    def test_bind_partial_failure(self, mock_method):
        # Arrange
        bound_method = BoundAnnouncementMethod(mock_method)
        # Act + Assert
        with pytest.raises(PartialBindException):
            bound_method.bind_partial(1, 2, foo="bar", extra="invalid")

    def test_execute(self):
        # Arrange
        instance = MagicMock()
        instance.method.return_value = "Executed"
        bound_method = BoundAnnouncementMethod(
            instance.method, MockInstrument()
        )
        # Act
        result = bound_method.execute()
        # Assert
        assert result == "Executed"

    def test_repr(self, mock_method):
        # Arrange
        mock_instrument = MockInstrument()
        bound_method = BoundAnnouncementMethod(
            mock_method, instrument=mock_instrument
        )
        # Act
        meth_repr = repr(bound_method)
        # Assert
        expected_repr = (
            f"BoundAnnouncementMethod(method={mock_method!r}, "
            f"instrument={mock_instrument!r})"
        )
        assert meth_repr == expected_repr
