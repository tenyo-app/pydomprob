class TestDecoratorImports:
    def test_announcement_decorator(self):
        # Arrange
        from domprob import sensor as alias_announcement
        from domprob.sensors.dec import sensor

        # Act
        # Assert
        assert alias_announcement is sensor
