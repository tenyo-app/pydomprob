import pytest

from domprob.announcements.decorators import Announcement, announcement
from domprob.announcements.validation.orchestrator import (
    AnnouncementValidationOrchestrator,
)
from domprob.announcements.validation.validators import InstrumentTypeException
from domprob.instrument import BaseInstrument


class MockInstrument(BaseInstrument):
    pass


@pytest.fixture
def mock_cls():
    """Fixture to provide a mock class for decoration."""

    class Cls:
        def method(self, instrument: MockInstrument):
            return f"Instrument: {instrument}"

    return Cls


@pytest.fixture
def announcement_instance():
    """Fixture for creating an Announcement instance."""
    return Announcement(MockInstrument, required=True)


class TestAnnouncement:
    def test_initialisation(self):
        """Test that Announcement is initialised correctly."""
        ann = Announcement(MockInstrument, required=False)
        assert ann.instrument is MockInstrument
        assert ann.required is False

    def test_repr(self):
        """Test the string representation of Announcement."""
        ann = Announcement(MockInstrument, required=True)
        expected_repr = (
            f"Announcement(instrument={MockInstrument!r}, required=True)"
        )
        assert repr(ann) == expected_repr

    def test_validater_property(self, announcement_instance):
        """Test that the `validater` property returns the orchestrator."""
        validater = announcement_instance.validater
        assert isinstance(validater, AnnouncementValidationOrchestrator)

    def test_call_method_executes_correctly(
        self, mock_cls, announcement_instance
    ):
        # Arrange
        mock_cls.method = announcement_instance(
            mock_cls.method
        )  # Decorate method
        instance = mock_cls()
        instrument = MockInstrument()
        # Act
        result = instance.method(instrument)
        # Assert
        assert result == f"Instrument: {instrument!r}"

    def test_call_method_raises_exception_on_invalid_instrument(
        self, mock_cls, announcement_instance
    ):
        """Test that the decorated method raises an exception for invalid instrument."""
        # Arrange
        mock_cls.method = announcement_instance(
            mock_cls.method
        )  # Decorate method
        instance = mock_cls()
        # Act
        with pytest.raises(InstrumentTypeException) as exc_info:
            instance.method("invalid instrument")
        # Assert
        assert (
            str(exc_info.value)
            == "Cls.method(...) expects 'instrument' param to be one of: "
            "[MockInstrument], but got: 'invalid instrument'"
        )


def test_announcement_lower_is_announcement_cls():
    assert announcement == Announcement
