from typing import TypeVar

import pytest

from domprob import get_probe, announcement, BaseObservation


@pytest.fixture
def mock_instrument_cls():
    class MockInstrument:

        msgs: list[str] = []

        def store(self, msg: str) -> None:
            self.msgs.append(msg)

    return MockInstrument


_Obs = TypeVar("_Obs", bound="ObserverProtocol")


@pytest.fixture
def mock_observation_cls(mock_instrument_cls) -> type[_Obs]:
    class MockObservation(BaseObservation):

        @announcement(mock_instrument_cls)
        def mock_announcement(self, mock_instrum: mock_instrument_cls) -> None:
            mock_instrum.store("Announcement!")

        @announcement(mock_instrument_cls)
        @announcement(mock_instrument_cls)
        def mock_announcement_again(
            self, mock_instrum: mock_instrument_cls
        ) -> None:
            mock_instrum.store("Stacked announcement!")

    return MockObservation


class TestProbe:
    def test_observe(self, mock_instrument_cls, mock_observation_cls):
        # Arrange
        instrum = mock_instrument_cls()
        probe_ = get_probe(instrum)
        # Act
        probe_.observe(mock_observation_cls())
        # Assert
        assert len(instrum.msgs) == 3, "Mock instrument not called"
        assert "Announcement!" in instrum.msgs
        assert "Stacked announcement!" in instrum.msgs
        assert "Stacked announcement!" in instrum.msgs
