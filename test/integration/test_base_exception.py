class TestBaseExceptionImport:
    def test_domprob_exception(self):
        # Arrange
        from domprob.base_exc import DomprobException
        from domprob.exceptions import (
            DomprobException as AliasDomprobException,
        )

        # Act
        # Assert
        assert AliasDomprobException is DomprobException
