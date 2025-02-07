from typing import Generator

import pytest

from domprob.announcements.method import AnnouncementMethod
from domprob.observations.observation import ObservationProtocol


class ProtocolImplementation:
    @classmethod
    def announcements(cls) -> Generator[AnnouncementMethod, None, None]:
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
