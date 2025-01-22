from typing import Any, TypeVar

import pytest

from domprob.announcements.instruments import Instruments
from domprob.announcements.metadata import AnnouncementMetadata
from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.orchestrator import (
    AnnouncementValidationOrchestrator,
)
from domprob.announcements.validation.validators import (
    InstrumentTypeException,
    MissingInstrumentException,
    NoSupportedInstrumentsException,
)


class MockInstrument:
    pass


class AnotherMockInstrument:
    pass


class YetAnotherMockInstrument:
    pass


@pytest.fixture
def orchestrator():
    return AnnouncementValidationOrchestrator


@pytest.fixture
def method():
    class Observation:
        def method(self, instrument: MockInstrument) -> None:
            pass

    return Observation().method


T = TypeVar("T", bound=BoundAnnouncementMethod)


def add_supported_instruments(method: T, *instruments: Any) -> T:
    metadata = AnnouncementMetadata(method)
    instrument_collection = Instruments(metadata)
    for instrument in instruments:
        instrument_collection.record(instrument)
    method._instruments = instrument_collection
    return method


class TestValidation:

    def test_single_supported_instrument(self, orchestrator, method):
        # Arrange
        bound_method = BoundAnnouncementMethod(method, MockInstrument())
        bound_method = add_supported_instruments(bound_method, MockInstrument)
        orchestrator = orchestrator()
        # Act
        orchestrator.validate(bound_method)  # Should not raise
        # Assert
        assert len(bound_method.instruments) == 1

    def test_multiple_supported_instruments(self, orchestrator, method):
        # Arrange
        bound_method = BoundAnnouncementMethod(method, MockInstrument())
        bound_method = add_supported_instruments(
            bound_method,
            MockInstrument,
            AnotherMockInstrument,
            YetAnotherMockInstrument,
        )
        orchestrator = orchestrator()
        # Act
        orchestrator.validate(bound_method)  # Should not raise
        # Assert
        assert len(bound_method.instruments) == 3

    def test_duplicate_supported_instruments(self, orchestrator, method):
        # Arrange
        bound_method = BoundAnnouncementMethod(method, MockInstrument())
        bound_method = add_supported_instruments(
            bound_method, MockInstrument, MockInstrument
        )
        orchestrator = orchestrator()
        # Act
        orchestrator.validate(bound_method)  # Should not raise
        # Assert
        assert len(bound_method.instruments) == 2

    def test_no_supported_instruments(self, orchestrator, method):
        # Arrange
        instrument = MockInstrument()
        bound_method = BoundAnnouncementMethod(method, instrument)
        orchestrator = orchestrator()
        # Act
        with pytest.raises(NoSupportedInstrumentsException) as exc_info:
            orchestrator.validate(bound_method)
        # Assert
        assert (
            str(exc_info.value)
            == f"Observation.method(...) has no supported instrument types "
            f"defined"
        )

    def test_unsupported_instrument(self, orchestrator, method):
        # Arrange
        instrument = MockInstrument()
        bound_method = BoundAnnouncementMethod(method, instrument)
        bound_method = add_supported_instruments(
            bound_method, AnotherMockInstrument
        )
        orchestrator = orchestrator()
        # Act
        with pytest.raises(InstrumentTypeException) as exc_info:
            orchestrator.validate(bound_method)
        # Assert
        assert (
            str(exc_info.value)
            == f"Observation.method(...) expects 'instrument' param "
            f"to be one of: [AnotherMockInstrument], but got: {instrument!r}"
        )

    def test_no_instrument_instance(self, orchestrator, method):
        # Arrange
        bound_method = BoundAnnouncementMethod(method)
        bound_method = add_supported_instruments(bound_method, MockInstrument)
        orchestrator = orchestrator()
        # Act
        with pytest.raises(MissingInstrumentException) as exc_info:
            orchestrator.validate(bound_method)
        # Assert
        assert (
            str(exc_info.value)
            == "'instrument' param missing in Observation.method(...)"
        )
