from collections.abc import Generator
from typing import TypeVar
from unittest.mock import MagicMock

import pytest

from domprob.announcements.method import AnnouncementMethod
from domprob.announcements.decorators import announcement
from domprob.probes.probe import probe, Probe, _INSTRUMENTS


@pytest.fixture
def mock_instrument_cls():
    class MockInstrument:

        msgs: list[str] = []

        def store(self, msg: str) -> None:
            self.msgs.append(msg)

    return MockInstrument


_Disp = TypeVar("_Disp", bound="DispatcherProtocol")


@pytest.fixture
def mock_dispatcher_cls() -> type[_Disp]:
    class MockDispatcher:
        def __init__(self, *mock_instruments):
            self.mock_instruments = mock_instruments

        def dispatch(self, observation):
            observation.mock_announcement(self.mock_instruments[0])

    return MockDispatcher


_Obs = TypeVar("_Obs", bound="ObserverProtocol")


@pytest.fixture
def mock_observation_cls(
    mock_instrument_cls, mock_dispatcher_cls
) -> type[_Obs]:
    class MockObservation:

        @announcement(mock_instrument_cls)
        def mock_announcement(
            self, mock_instrument: mock_instrument_cls
        ) -> None:
            mock_instrument.store("announcement!")

        def announcements(self) -> Generator[AnnouncementMethod, None, None]:
            yield AnnouncementMethod(self.mock_announcement)

    return MockObservation


class TestProbe:

    def test_init(self, mock_instrument_cls, mock_dispatcher_cls):
        # Arrange
        mock_instrum = mock_instrument_cls()
        mock_dispatcher = mock_dispatcher_cls(mock_instrum)
        # Act
        mock_probe = Probe(mock_dispatcher)
        # Assert
        assert mock_probe.dispatcher == mock_dispatcher

    def test_probe_equality_same_instance(self, mock_dispatcher_cls):
        # Arrange
        mock_dispatcher = mock_dispatcher_cls()
        probe1 = Probe(mock_dispatcher)
        probe2 = Probe(mock_dispatcher)
        # Act + # Assert
        assert probe1 == probe2

    def test_probe_equality_different_dispatcher(self, mock_dispatcher_cls):
        # Arrange
        probe1 = Probe(mock_dispatcher_cls())
        probe2 = Probe(MagicMock())
        # Act + Assert
        assert probe1 != probe2

    def test_probe_equality_different_type(self, mock_dispatcher_cls):
        # Arrange
        probe1 = Probe(mock_dispatcher_cls())
        other = object()
        # Act + Assert
        assert probe1 != other

    def test_probe_equality_subclass(self, mock_dispatcher_cls):
        # Arrange
        class SubProbe(Probe):
            pass

        mock_dispatcher = mock_dispatcher_cls()
        probe1 = Probe(mock_dispatcher)
        probe2 = SubProbe(mock_dispatcher)
        # Act + Assert
        assert probe1 != probe2

    def test_probe_hash_same_dispatcher(self):
        # Arrange
        mock_dispatcher = MagicMock()
        probe1 = Probe(mock_dispatcher)
        probe2 = Probe(mock_dispatcher)
        # Act
        probe1_hash = hash(probe1)
        probe2_hash = hash(probe2)
        # Assert
        assert probe1_hash == probe2_hash
        assert hash(probe1) == hash(probe2)

    def test_probe_hash_different_dispatchers(self):
        # Arrange
        probe1 = Probe(MagicMock())
        probe2 = Probe(MagicMock)
        # Act
        probe1_hash = hash(probe1)
        probe2_hash = hash(probe2)
        # Assert
        assert probe1_hash != probe2_hash

    def test_probe_hashability_set(self):
        # Arrange
        mock_dispatcher = MagicMock()
        probe1 = Probe(mock_dispatcher)
        probe2 = Probe(mock_dispatcher)
        # Act
        probe_set = {probe1, probe2}
        # Assert
        assert len(probe_set) == 1

    def test_probe_hashability_dict(self):
        # Arrange
        mock_dispatcher = MagicMock()
        probe1 = Probe(mock_dispatcher)
        probe2 = Probe(mock_dispatcher)
        # Act
        probe_dict = {probe1: "value"}
        # Assert
        assert probe_dict[probe2] == "value"

    def test_observe(
        self, mock_instrument_cls, mock_dispatcher_cls, mock_observation_cls
    ):
        # Arrange
        mock_instrum = mock_instrument_cls()
        mock_dispatcher = mock_dispatcher_cls(mock_instrum)
        mock_probe = Probe(mock_dispatcher)
        # Act
        mock_probe.observe(mock_observation_cls())
        # Assert
        assert len(mock_instrum.msgs) == 1, "Mock instrument not called"
        assert mock_instrum.msgs[0] == "announcement!"

    def test_repr(self, mock_instrument_cls, mock_dispatcher_cls):
        # Arrange
        mock_instrum = mock_instrument_cls()
        mock_dispatcher = mock_dispatcher_cls(mock_instrum)
        mock_probe = Probe(mock_dispatcher)
        # Act
        mock_probe_repr = repr(mock_probe)
        # Assert
        assert mock_probe_repr == f"Probe(dispatcher={mock_dispatcher!r})"


def test_probe_with_instruments(mock_instrument_cls, mocker):
    # Arrange
    mock_dispatcher = mocker.patch("domprob.probes.probe.BasicDispatcher")
    mock_probe = mocker.patch("domprob.probes.probe.Probe")
    mock_instrument = mock_instrument_cls()
    # Act
    result = probe(mock_instrument)
    actual_instrums = result.dispatcher.mock_instruments
    # Assert
    mock_dispatcher.assert_called_once_with((mock_instrument,))
    mock_probe.assert_called_once_with(mock_dispatcher.return_value)
    assert result == mock_probe.return_value


def test_probe_with_no_instruments(mocker):
    # Arrange
    mock_dispatcher = mocker.patch("domprob.probes.probe.BasicDispatcher")
    mock_probe = mocker.patch("domprob.probes.probe.Probe")
    # Act
    result = probe()
    # Assert
    mock_dispatcher.assert_called_once_with(_INSTRUMENTS)
    mock_probe.assert_called_once_with(mock_dispatcher.return_value)
    assert result == mock_probe.return_value
