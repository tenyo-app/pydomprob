from typing import Generator

import pytest

from domprob.observations.observation import ObservationProtocol
from domprob.sensors.meth import SensorMethod


class ProtocolImplementation:
    @classmethod
    def sensors(cls) -> Generator[SensorMethod, None, None]:
        pass


@pytest.fixture
def protocol_imp():
    return ProtocolImplementation()


class WrongProtocolImplementation:
    pass


@pytest.fixture
def wrong_protocol_imp():
    return WrongProtocolImplementation()


class TestObservationProtocol:
    def test_correct_protocol_implementation(self, protocol_imp):
        # Arrange
        # Act
        # Assert
        assert isinstance(protocol_imp, ObservationProtocol)

    def test_incorrect_protocol_implementation(self, wrong_protocol_imp):
        # Arrange
        # Act
        # Assert
        assert not isinstance(wrong_protocol_imp, ObservationProtocol)
