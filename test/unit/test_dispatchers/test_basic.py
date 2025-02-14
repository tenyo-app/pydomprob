import copy

import pytest
from unittest.mock import Mock
from typing import Any, TypeVar

from domprob import BaseObservation, announcement
from domprob.announcements.method import AnnouncementMethod
from domprob.dispatchers.basic import (
    InstrumentImpRegistry,
    BasicDispatcher,
    ReqInstrumException,
)

_Instrument = TypeVar("_Instrument", bound=Any)


class MockInstrument:
    @staticmethod
    def action():
        return "Instrument action"


class MockObservation(BaseObservation):
    called = 0
    obs = None
    instrum = None

    @announcement(MockInstrument)
    def foo(self, db):
        self.called += 1
        self.obs = self
        self.instrum = db


class MockObservationWithRequired(BaseObservation):
    @announcement(MockInstrument, required=True)
    def foo(self, instrument: MockInstrument):
        pass


class MockAnnouncementMethod(AnnouncementMethod):
    def __init__(self):
        super().__init__(Mock())
        self._supp_instrums = [(MockInstrument, False)]


class UnhashableMeta(type):
    def __hash__(cls):
        raise TypeError(f"Cannot hash class {cls.__name__}")


class UnhashableInstrument(metaclass=UnhashableMeta):
    pass


class TestInstrumentImpRegistry:
    def test_registry_initialization(self):
        # Arrange
        instrum1 = MockInstrument()
        instrum2 = MockInstrument()
        # Act
        registry = InstrumentImpRegistry(instrum1, instrum2)
        # Assert
        assert len(registry) == 2
        assert instrum1 in registry
        assert instrum2 in registry

    def test_registry_get_existing_instrument(self):
        # Arrange
        instrum = MockInstrument()
        registry = InstrumentImpRegistry(instrum)
        # Act
        retrieved = registry.get(MockInstrument)
        # Assert
        assert retrieved is instrum

    def test_registry_cache(self):
        # Arrange
        instrum = MockInstrument()
        registry = InstrumentImpRegistry(instrum)
        cache_before = copy.deepcopy(registry._cache)
        # Act
        _ = registry.get(MockInstrument)
        cache_after = registry._cache
        # Assert
        assert MockInstrument not in cache_before
        assert MockInstrument in cache_after

    def test_registry_get_missing_instrument(self):
        # Arrange
        registry = InstrumentImpRegistry()
        # Act
        instrum = registry.get(MockInstrument)
        # Asert
        assert instrum is None

    def test_registry_get_cached_instrument(self):
        # Arrange
        instrum = MockInstrument()
        registry = InstrumentImpRegistry(instrum)
        # Act
        retrieved = registry.get(MockInstrument)
        cache_before = copy.deepcopy(registry._cache)
        retrieved_again = registry.get(MockInstrument)
        cache_after = registry._cache
        # Assert
        assert retrieved is retrieved_again
        assert len(cache_after) == 1
        assert len(cache_before) == len(cache_after)

    def test_registry_get_required_instrument(self):
        # Arrange
        registry = InstrumentImpRegistry()
        # Act
        with pytest.raises(KeyError) as exc:
            registry.get(MockInstrument, required=True)
        # Assert
        assert str(exc.value) == (
            "'Instrument `MockInstrument` not found in available "
            "implementations: None'"
        )

    def test_registry_handles_unhashable_types(self):
        # Arrange
        instrum = UnhashableInstrument()
        registry = InstrumentImpRegistry(instrum)
        # Act
        retrieved = registry.get(UnhashableInstrument)
        # Assert
        assert retrieved is instrum
        assert len(registry._cache) == 0

    def test_repr(self):
        # Arrange
        instrum = UnhashableInstrument()
        registry = InstrumentImpRegistry(instrum)
        # Act
        registry_repr = repr(registry)
        # Assert
        assert registry_repr == "InstrumentImpRegistry(num_instruments=1)"


class TestBasicDispatcher:

    def test_dispatcher_initialization(self):
        # Arrange
        instrum = MockInstrument()
        # Act
        dispatcher = BasicDispatcher(instrum)
        # Assert
        assert len(dispatcher.instrums) == 1
        assert dispatcher.instrums.get(MockInstrument) is instrum

    def test_dispatcher_equality_same_instruments(self):
        # Arrange
        instrum = MockInstrument()
        dispatcher1 = BasicDispatcher(instrum)
        dispatcher2 = BasicDispatcher(instrum)
        # Act + Assert
        assert dispatcher1 == dispatcher2

    def test_dispatcher_equality_different_instruments(self):
        # Arrange
        dispatcher1 = BasicDispatcher(MockInstrument())
        dispatcher2 = BasicDispatcher(MockInstrument())
        # Act + Assert
        assert dispatcher1 != dispatcher2

    def test_dispatcher_equality_different_type(self):
        # Arrange
        dispatcher = BasicDispatcher(MockInstrument())
        # Act + Assert
        assert dispatcher != object()

    def test_dispatcher_equality_subclass(self):
        # Arrange
        class SubDispatcher(BasicDispatcher):
            pass

        instrum = MockInstrument()
        dispatcher1 = BasicDispatcher(instrum)
        dispatcher2 = SubDispatcher(instrum)
        # Act + Assert
        assert dispatcher1 != dispatcher2

    def test_dispatcher_hash_same_instruments(self):
        # Arrange
        instrum = MockInstrument()
        dispatcher1 = BasicDispatcher(instrum)
        dispatcher2 = BasicDispatcher(instrum)
        # Act
        hash_dispatcher1 = hash(dispatcher1)
        hash_dispatcher2 = hash(dispatcher2)
        # Assert
        assert hash_dispatcher1 == hash_dispatcher2

    def test_dispatcher_hash_different_instruments(self):
        # Arrange
        dispatcher1 = BasicDispatcher(MockInstrument())
        dispatcher2 = BasicDispatcher(MockInstrument())
        # Act
        hash_dispatcher1 = hash(dispatcher1)
        hash_dispatcher2 = hash(dispatcher2)
        # Assert
        assert hash_dispatcher1 != hash_dispatcher2

    def test_dispatcher_hashability_set(self):
        # Arrange
        instrum = MockInstrument()
        dispatcher1 = BasicDispatcher(instrum)
        dispatcher2 = BasicDispatcher(instrum)
        # Act
        dispatcher_set = {dispatcher1, dispatcher2}
        # Assert
        assert len(dispatcher_set) == 1

    def test_dispatcher_hashability_dict(self):
        # Arrange
        instrum = MockInstrument()
        dispatcher1 = BasicDispatcher(instrum)
        dispatcher2 = BasicDispatcher(instrum)
        # Act
        dispatcher_dict = {dispatcher1: "value"}
        # Assert
        assert dispatcher_dict[dispatcher2] == "value"

    def test_dispatcher_handles_multiple_instruments(self):
        # Arrange
        instrum1 = MockInstrument()
        instrum2 = MockInstrument()
        # Act
        dispatcher = BasicDispatcher(instrum1, instrum2)
        # Assert
        assert len(dispatcher.instrums) == 2
        assert dispatcher.instrums.get(MockInstrument) in {instrum1, instrum2}

    def test_dispatcher_announcement(self):
        # Arrange
        instrum = MockInstrument()
        dispatcher = BasicDispatcher(instrum)
        observation = MockObservation()
        # Act
        dispatcher.dispatch(observation)  # type: ignore
        # Assert
        assert observation.called == 1
        assert observation.obs == observation
        assert observation.instrum == instrum

    def test_dispatcher_handles_missing_instrument(self):
        # Arrange
        dispatcher = BasicDispatcher()
        observation = MockObservation()
        # Act
        dispatcher.dispatch(observation)  # type: ignore
        # Assert
        assert observation.called == 0

    def test_dispatcher_required_missing_instrument(self):
        # Arrange
        dispatcher = BasicDispatcher()
        observation = MockObservationWithRequired()
        # Act
        with pytest.raises(ReqInstrumException) as exc:
            dispatcher.dispatch(observation)  # type: ignore
        # Assert
        assert str(exc.value) == (
            "Required instrument `MockInstrument` in "
            "`MockObservationWithRequired.foo(...)` is missing from available "
            "implementations: None"
        )

    def test_dispatcher_handles_unhashable_instrument(self):
        # Arrange
        instrum = UnhashableInstrument()
        # Act
        dispatcher = BasicDispatcher(instrum)
        # Assert
        assert dispatcher.instrums.get(UnhashableInstrument) is instrum
        assert len(dispatcher.instrums._cache) == 0

    def test_dispatcher_repr(self):
        # Arrange
        instrum = MockInstrument()
        dispatcher = BasicDispatcher(instrum)
        # Act
        dispatcher_repr = repr(dispatcher)
        # Assert
        assert "BasicDispatcher" in dispatcher_repr
        assert "MockInstrument" in dispatcher_repr
