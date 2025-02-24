import copy

import pytest

from domprob import BaseObservation, sensor
from domprob.consumers.basic import (
    BasicConsumer,
    InstrumentImpRegistry,
    ReqInstrumException,
)


class MockInstrument:
    @staticmethod
    def action():
        return "Instrument action"


class MockObservation(BaseObservation):
    called = 0
    obs = None
    instrum = None

    @sensor(MockInstrument)
    def foo(self, db):
        self.called += 1
        self.obs = self
        self.instrum = db


class MockObservationWithRequired(BaseObservation):
    @sensor(MockInstrument, required=True)
    def foo(self, instrum: MockInstrument):
        pass


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


class TestBasicConsumer:

    def test_consumer_init(self):
        # Arrange
        instrum = MockInstrument()
        # Act
        consumer = BasicConsumer(instrum)
        # Assert
        assert len(consumer.instrums) == 1
        assert consumer.instrums.get(MockInstrument) is instrum

    def test_consumer_equality_same_instruments(self):
        # Arrange
        instrum = MockInstrument()
        consumer1 = BasicConsumer(instrum)
        consumer2 = BasicConsumer(instrum)
        # Act + Assert
        assert consumer1 == consumer2

    def test_consumer_equality_different_instruments(self):
        # Arrange
        consumer1 = BasicConsumer(MockInstrument())
        consumer2 = BasicConsumer(MockInstrument())
        # Act + Assert
        assert consumer1 != consumer2

    def test_consumer_equality_different_type(self):
        # Arrange
        consumer = BasicConsumer(MockInstrument())
        # Act + Assert
        assert consumer != object()

    def test_consumer_equality_subclass(self):
        # Arrange
        class SubConsumer(BasicConsumer):
            pass

        instrum = MockInstrument()
        consumer1 = BasicConsumer(instrum)
        consumer2 = SubConsumer(instrum)
        # Act + Assert
        assert consumer1 != consumer2

    def test_consumer_hash_same_instruments(self):
        # Arrange
        instrum = MockInstrument()
        consumer1 = BasicConsumer(instrum)
        consumer2 = BasicConsumer(instrum)
        # Act
        hash_consumer1 = hash(consumer1)
        hash_consumer2 = hash(consumer2)
        # Assert
        assert hash_consumer1 == hash_consumer2

    def test_consumer_hash_different_instruments(self):
        # Arrange
        consumer1 = BasicConsumer(MockInstrument())
        consumer2 = BasicConsumer(MockInstrument())
        # Act
        hash_consumer1 = hash(consumer1)
        hash_consumer2 = hash(consumer2)
        # Assert
        assert hash_consumer1 != hash_consumer2

    def test_consumer_hashability_set(self):
        # Arrange
        instrum = MockInstrument()
        consumer1 = BasicConsumer(instrum)
        consumer2 = BasicConsumer(instrum)
        # Act
        consumer_set = {consumer1, consumer2}
        # Assert
        assert len(consumer_set) == 1

    def test_consumer_hashability_dict(self):
        # Arrange
        instrum = MockInstrument()
        consumer1 = BasicConsumer(instrum)
        consumer2 = BasicConsumer(instrum)
        # Act
        dispatcher_dict = {consumer1: "value"}
        # Assert
        assert dispatcher_dict[consumer2] == "value"

    def test_consumer_handles_multiple_instruments(self):
        # Arrange
        instrum1 = MockInstrument()
        instrum2 = MockInstrument()
        # Act
        consumer = BasicConsumer(instrum1, instrum2)
        # Assert
        assert len(consumer.instrums) == 2
        assert consumer.instrums.get(MockInstrument) in {instrum1, instrum2}

    def test_consumer_sensor(self):
        # Arrange
        instrum = MockInstrument()
        consumer = BasicConsumer(instrum)
        observation = MockObservation()
        # Act
        consumer.consume(observation)  # type: ignore
        # Assert
        assert observation.called == 1
        assert observation.obs == observation
        assert observation.instrum == instrum

    def test_consumer_handles_missing_instrument(self):
        # Arrange
        consumer = BasicConsumer()
        observation = MockObservation()
        # Act
        consumer.consume(observation)  # type: ignore
        # Assert
        assert observation.called == 0

    def test_consumer_required_missing_instrument(self):
        # Arrange
        consumer = BasicConsumer()
        observation = MockObservationWithRequired()
        # Act
        with pytest.raises(ReqInstrumException) as exc:
            consumer.consume(observation)  # type: ignore
        # Assert
        assert str(exc.value) == (
            "Required instrument `MockInstrument` in "
            "`MockObservationWithRequired.foo(...)` is missing from available "
            "implementations: None"
        )

    def test_consumer_handles_unhashable_instrument(self):
        # Arrange
        instrum = UnhashableInstrument()
        # Act
        consumer = BasicConsumer(instrum)
        # Assert
        assert consumer.instrums.get(UnhashableInstrument) is instrum
        assert len(consumer.instrums._cache) == 0

    def test_consumer_repr(self):
        # Arrange
        instrum = MockInstrument()
        consumer = BasicConsumer(instrum)
        # Act
        consumer_repr = repr(consumer)
        # Assert
        assert "BasicConsumer" in consumer_repr
        assert "MockInstrument" in consumer_repr
