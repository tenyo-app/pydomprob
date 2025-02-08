class TestBaseExceptionImport:
    def test_domprob_exception(self):
        # Arrange
        from domprob.exceptions import DomprobException as AliasDomprobException
        from domprob.base_exc import DomprobException
        # Act
        # Assert
        assert AliasDomprobException is DomprobException
