class TestObservationImports:
    def test_base_observation_cls(self):
        # Arrange
        from domprob import BaseObservation as AliasedBaseObservation
        from domprob.observations.base import BaseObservation

        # Act
        # Assert
        assert AliasedBaseObservation is BaseObservation
