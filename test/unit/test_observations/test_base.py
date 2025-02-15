import pytest

from domprob.announcements.method import AnnouncementMethod
from domprob import announcement
from domprob.observations.base import BaseObservation, AnnouncementSet
from domprob.observations.observation import ObservationProtocol


class MockObservation(BaseObservation):

    def __init__(self):
        self.called = False

    @announcement("mock_instrument")  # type: ignore
    def sample_announcement(self, _: str):
        self.called = True
        return "Hello, Observer!"


@pytest.fixture
def observation_cls():
    return MockObservation


class TestAnnouncementSet:

    def test_init(self, observation_cls):
        # Arrange
        meth = AnnouncementMethod(observation_cls.sample_announcement)
        # Act
        announcements = AnnouncementSet(meth, meth)
        # Assert
        assert len(announcements._announcement_methods) == 1
        assert announcements._announcement_methods == {meth}

    def test_from_observation_cls_method(self, observation_cls):
        # Arrange
        # Act
        announcements = AnnouncementSet.from_observation(observation_cls)
        # Assert
        assert len(announcements._announcement_methods) == 1
        meth, = announcements._announcement_methods
        assert meth.meth == observation_cls.sample_announcement

    def test_contains(self, observation_cls):
        # Arrange
        meth = AnnouncementMethod(observation_cls.sample_announcement)
        # Act
        announcements = AnnouncementSet(meth, meth)
        # Assert
        assert meth in announcements
        assert "" not in announcements
        assert AnnouncementMethod(lambda: ...) not in announcements

    def test_iter(self, observation_cls):
        # Arrange
        meth = AnnouncementMethod(observation_cls.sample_announcement)
        # Act
        announcement_set = AnnouncementSet(meth, meth)
        # Assert
        assert set(iter(announcement_set)) == {meth, meth}

    def test_len(self, observation_cls):
        # Arrange
        meth = AnnouncementMethod(observation_cls.sample_announcement)
        # Act
        announcements = AnnouncementSet(meth, meth)
        # Assert
        assert len(announcements) == 1

    def test_repr(self, observation_cls):
        # Arrange
        meth = AnnouncementMethod(observation_cls.sample_announcement)
        announcements = AnnouncementSet(meth, meth)
        # Act
        announcements_repr = repr(announcements)
        # Assert
        assert announcements_repr == 'AnnouncementSet(num_announcements=1)'


class TestBaseObservation:

    def test_follows_observation_protocol(self, observation_cls):
        # Arrange
        observation = observation_cls()
        # Act
        # Assert
        assert isinstance(observation, BaseObservation)
        assert isinstance(observation, ObservationProtocol)

    def test_announcements_generator(self, observation_cls):
        # Arrange
        # Act
        announcements = list(observation_cls.announcements())
        # Assert
        assert len(announcements) == 1
        assert isinstance(announcements[0], AnnouncementMethod)
        assert announcements[0].meth == observation_cls.sample_announcement

    def test_announcements_caching(self, observation_cls):
        # Arrange
        old_announcement = list(observation_cls.announcements())[0]

        # Act
        def new_announcement():
            return "New announcement"

        observation_cls.new_announcement = new_announcement
        cached_announcements = list(observation_cls.announcements())
        # Assert
        assert len(cached_announcements) == 1
        assert cached_announcements[0] == old_announcement

    def test_len_method(self, observation_cls):
        # Arrange
        # Act
        num_announcements = len(observation_cls())
        # Assert
        assert num_announcements == 1

    def test_repr_method(self, observation_cls):
        # Arrange
        # Act
        obs_repr = repr(observation_cls())
        # Assert
        assert obs_repr == "MockObservation(announcements=1)"
