from typing import ParamSpec, TypeVar, Generic

import pytest

from domprob.dispatchers.dispatcher import DispatcherProtocol, _P, _R
from domprob.observations.observation import ObservationProtocol


class ProtocolImplementation:
    def dispatch(
        self, observation: ObservationProtocol[[_P.args, _P.kwargs], _R]
    ) -> _R:
        pass


@pytest.fixture
def protocol_imp():
    return ProtocolImplementation()


class WrongProtocolImplementation:
    pass


@pytest.fixture
def wrong_protocol_imp():
    return WrongProtocolImplementation()


class TestDispatcherProtocol:
    def test_correct_protocol_implementation(self, protocol_imp):
        # Arrange
        # Act
        # Assert
        assert isinstance(protocol_imp, DispatcherProtocol)

    def test_incorrect_protocol_implementation(self, wrong_protocol_imp):
        # Arrange
        # Act
        # Assert
        assert not isinstance(wrong_protocol_imp, DispatcherProtocol)
