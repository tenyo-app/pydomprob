class TestDecoratorImports:
    def test_announcement_decorator(self):
        # Arrange
        from domprob import announcement as alias_announcement
        from domprob.announcements.decorators import announcement

        # Act
        # Assert
        assert alias_announcement is announcement
