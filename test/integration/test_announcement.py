class TestDecoratorImports:
    def test_announcement_decorator(self):
        # Arrange
        from domprob import announce as alias_announcement
        from domprob.announcement.dec import announce

        # Act
        # Assert
        assert alias_announcement is announce
