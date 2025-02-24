from typing import TypeVar

import pytest

from domprob import BaseObservation, get_probe, sensor


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

        @sensor(mock_instrument_cls)
        def mock_sensor(self, mock_instrum: mock_instrument_cls) -> None:
            mock_instrum.store("Sensed!")

        @staticmethod
        @sensor(mock_instrument_cls)
        def mock_static_sensor(mock_instrum: mock_instrument_cls) -> None:
            mock_instrum.store("Sensed static!")

        @sensor(mock_instrument_cls)
        @sensor(mock_instrument_cls)
        def mock_sensor_stacked(
            self, mock_instrum: mock_instrument_cls
        ) -> None:
            mock_instrum.store("Stacked sensed!")

        @staticmethod
        @sensor(mock_instrument_cls)
        @sensor(mock_instrument_cls)
        def mock_static_sensor_stacked(
            mock_instrum: mock_instrument_cls,
        ) -> None:
            mock_instrum.store("Stacked static sensed!")

    return MockObservation


class TestProbe:
    def test_observe(self, mock_instrument_cls, mock_observation_cls):
        # Arrange
        instrum = mock_instrument_cls()
        probe_ = get_probe(instrum)
        # Act
        probe_.observe(mock_observation_cls())
        # Assert
        assert len(instrum.msgs) == 6, "Mock instrument not called correctly"
        assert len(set(instrum.msgs)) == 4
        assert "Sensed!" in instrum.msgs
        assert "Sensed static!" in instrum.msgs
        assert "Stacked sensed!" in instrum.msgs
        assert "Stacked static sensed!" in instrum.msgs
