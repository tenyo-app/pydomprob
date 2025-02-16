from typing import Any, Iterable

import pytest

from domprob.announcements.method import AnnouncementMethod
from domprob.consumers.consumer import ConsumerProtocol
from domprob import BasicDispatcher
from domprob.observations.observation import ObservationProtocol


class MockConsumer(ConsumerProtocol):
    consumed = []

    def __eq__(self, other: Any):
        pass

    def __hash__(self) -> int:
        return 1

    def consume(self, observation: ObservationProtocol) -> None:
        self.consumed.append(observation)


@pytest.fixture
def mock_consumer():
    return MockConsumer


class MockObservation(ObservationProtocol):
    @classmethod
    def announcements(cls) -> Iterable[AnnouncementMethod]:
        pass


@pytest.fixture
def mock_observation():
    return MockObservation


class TestBasicDispatcher:

    def test_init(self, mock_consumer):
        # Arrange
        consumer = mock_consumer()
        # Act
        dispatcher = BasicDispatcher(consumer)
        # Assert
        assert len(dispatcher.consumers) == 1

    def test_equality_same_consumers(self, mock_consumer):
        # Arrange
        consumer1 = mock_consumer()
        consumer2 = mock_consumer()
        dispatcher1 = BasicDispatcher(consumer1, consumer2)
        dispatcher2 = BasicDispatcher(consumer1, consumer2)
        # Act
        # Assert
        assert dispatcher1 == dispatcher2

    def test_equality_not_same_consumers(self, mock_consumer):
        # Arrange
        consumer1 = mock_consumer()
        consumer2 = mock_consumer()
        dispatcher1 = BasicDispatcher(consumer1, consumer2)
        dispatcher2 = BasicDispatcher(consumer1)
        # Act
        # Assert
        assert dispatcher1 != dispatcher2

    def test_equality_different_type(self, mock_consumer):
        # Arrange
        consumer1 = mock_consumer()
        consumer2 = mock_consumer()
        dispatcher = BasicDispatcher(consumer1, consumer2)
        # Act
        # Assert
        assert dispatcher != object()

    def test_equality_subclass(self, mock_consumer):
        # Arrange
        class AnotherDispatcher(BasicDispatcher):
            pass

        consumer1 = mock_consumer()
        consumer2 = mock_consumer()
        dispatcher1 = BasicDispatcher(consumer1, consumer2)
        dispatcher2 = AnotherDispatcher(consumer1, consumer2)
        # Act
        # Assert
        assert dispatcher1 != dispatcher2

    def test_hash_same_consumers(self, mock_consumer):
        # Arrange
        consumer1 = mock_consumer()
        consumer2 = mock_consumer()
        dispatcher1 = BasicDispatcher(consumer1, consumer2)
        dispatcher2 = BasicDispatcher(consumer1, consumer2)
        # Act
        # Assert
        assert hash(dispatcher1) == hash(dispatcher2)

    def test_hash_different_consumers(self, mock_consumer):
        # Arrange
        consumer1 = mock_consumer()
        consumer2 = mock_consumer()
        dispatcher1 = BasicDispatcher(consumer1, consumer2)
        dispatcher2 = BasicDispatcher(consumer1)
        # Act
        # Assert
        assert hash(dispatcher1) != hash(dispatcher2)

    def test_hashability_set(self, mock_consumer):
        # Arrange
        consumer1 = mock_consumer()
        consumer2 = mock_consumer()
        dispatcher1 = BasicDispatcher(consumer1, consumer2)
        dispatcher2 = BasicDispatcher(consumer1, consumer2)
        dispatcher_set = {dispatcher1, dispatcher2}
        # Act
        # Assert
        assert len(dispatcher_set) == 1

    def test_hashability_dict(self, mock_consumer):
        # Arrange
        consumer1 = mock_consumer()
        consumer2 = mock_consumer()
        dispatcher1 = BasicDispatcher(consumer1, consumer2)
        dispatcher2 = BasicDispatcher(consumer1, consumer2)
        dispatcher_dict = {dispatcher1: "value"}
        # Act
        # Assert
        assert dispatcher_dict[dispatcher2] == "value"

    def test_consume(self, mock_consumer, mock_observation):
        # Arrange
        consumer = mock_consumer()
        dispatcher = BasicDispatcher(consumer, consumer)
        # Act
        dispatcher.dispatch(mock_observation())
        # Assert
        assert len(consumer.consumed) == 2

    def test_repr(self, mock_consumer):
        # Arrange
        consumer = mock_consumer()
        dispatcher = BasicDispatcher(consumer)
        # Act
        dispatcher_repr = repr(dispatcher)
        # Assert
        assert "BasicDispatcher(" in dispatcher_repr
        assert "consumers=(<" in dispatcher_repr
