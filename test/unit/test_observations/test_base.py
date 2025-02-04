import pytest

from domprob.announcements.method import AnnouncementMethod
from domprob import announcement
from domprob.observations.base import _is_function, BaseObservation


def test_is_function_valid_function():
    # Arrange
    def sample_function():
        pass

    # Act
    is_func_result = _is_function(sample_function)
    # Assert
    assert is_func_result is True


def test_is_function_property_is_not_function():
    # Arrange
    class SampleClass:
        @property
        def sample_prop(self):
            return 42

    # Act
    is_func_result = _is_function(SampleClass.sample_prop)
    # Assert
    assert is_func_result is False


def test_is_function_cached_property_is_not_function():
    # Arrange
    from functools import cached_property

    class SampleClass:
        @cached_property
        def cached_prop(self):
            return 42

    # Act
    is_func_result = _is_function(SampleClass.cached_prop)
    # Assert
    assert is_func_result is False


def test_is_function_dunder_method_is_not_function():
    # Arrange
    class SampleClass:
        def __str__(self):
            return "Sample"

    # Act
    is_func_result = _is_function(SampleClass.__str__)
    # Assert
    assert is_func_result is False


class TestBaseObservation:

    class MockObservation(BaseObservation):

        def __init__(self):
            self.called = False

        @announcement("mock_instrument")  # type: ignore
        def sample_announcement(self, _: str):
            self.called = True
            return "Hello, Observer!"

    @pytest.fixture
    def observation_cls(self):
        return TestBaseObservation.MockObservation

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
        old_announcement =  list(observation_cls.announcements())[0]
        # Act
        def new_announcement():
            return "New announcement"

        observation_cls.new_announcement = new_announcement
        cached_announcements = list(observation_cls.announcements())
        # Assert
        assert len(cached_announcements) == 1
        assert cached_announcements[0] == old_announcement

    def test_instruments(self, observation_cls):
        # Arrange
        # Act
        instr_map = observation_cls.instruments()
        # Assert
        assert isinstance(instr_map, dict)
        assert "mock_instrument" in instr_map
        assert isinstance(instr_map["mock_instrument"], set)
        assert len(instr_map["mock_instrument"]) == 1

    def test_instruments_caching(self, observation_cls):
        # Arrange
        # Act
        first_call = observation_cls.instruments()
        second_call = observation_cls.instruments()
        # Assert
        assert first_call is second_call

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
