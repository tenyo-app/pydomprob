from typing import Any

import pytest

from domprob.consumers.consumer import ConsumerProtocol
from domprob.observations.observation import ObservationProtocol


class ProtocolImplementation:
    def __eq__(self, other: Any) -> bool:
        pass

    def __hash__(self) -> int:
        pass

    def consume(self, observation: ObservationProtocol) -> None:
        pass


@pytest.fixture
def protocol_imp():
    return ProtocolImplementation()


class WrongProtocolImplementation:
    pass


@pytest.fixture
def wrong_protocol_imp():
    return WrongProtocolImplementation()


class TestConsumerProtocol:
    def test_runnable_correct_protocol_implementation(self, protocol_imp):
        # Arrange
        # Act
        # Assert
        assert isinstance(protocol_imp, ConsumerProtocol)

    def test_runnable_incorrect_protocol_implementation(
        self, wrong_protocol_imp
    ):
        # Arrange
        # Act
        # Assert
        assert not isinstance(wrong_protocol_imp, ConsumerProtocol)
