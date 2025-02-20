class TestDispatcherExceptionImports:
    def test_base_dispatcher_exception(self):
        # Arrange
        from domprob.dispatchers.dispatcher import DispatcherException
        from domprob.exceptions import (
            DispatcherException as AliasDispatcherException,
        )

        # Act
        # Assert
        assert AliasDispatcherException is DispatcherException
