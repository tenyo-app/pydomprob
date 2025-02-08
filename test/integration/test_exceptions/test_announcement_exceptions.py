class TestAnnouncementExceptionImport:
    def test_announcement_exception(self):
        # Arrange
        from domprob.exceptions import AnnouncementException as AliasAnnouncementException
        from domprob.announcements.exceptions import AnnouncementException
        # Act
        # Assert
        assert AliasAnnouncementException is AnnouncementException


class TestAnnouncementMethodExceptionImport:

    def test_partial_bind_exception(self):
        # Arrange
        from domprob.exceptions import PartialBindException as AliasPartialBindException
        from domprob.announcements.method import PartialBindException
        # Act
        # Assert
        assert AliasPartialBindException is PartialBindException


class TestAnnouncementValidationExceptionImports:

    def test_validater_exception(self):
        # Arrange
        from domprob.exceptions import ValidatorException as AliasValidatorException
        from domprob.announcements.validation.validators import ValidatorException
        # Act
        # Assert
        assert AliasValidatorException is ValidatorException

    def test_instrum_type_exception(self):
        # Arrange
        from domprob.exceptions import InstrumTypeException as AliasInstrumTypeException
        from domprob.announcements.validation.validators import InstrumTypeException
        # Act
        # Assert
        assert AliasInstrumTypeException is InstrumTypeException

    def test_missing_instrum_exception(self):
        # Arrange
        from domprob.exceptions import MissingInstrumException as AliasMissingInstrumException
        from domprob.announcements.validation.validators import MissingInstrumException
        # Act
        # Assert
        assert AliasMissingInstrumException is MissingInstrumException

    def test_no_supported_instrums_exception(self):
        # Arrange
        from domprob.exceptions import NoSupportedInstrumsException as AliasNoSupportedInstrumsException
        from domprob.announcements.validation.validators import NoSupportedInstrumsException
        # Act
        # Assert
        assert AliasNoSupportedInstrumsException is NoSupportedInstrumsException


class TestAnnouncementChainExceptionImport:

    def test_empty_chain_exception(self):
        # Arrange
        from domprob.exceptions import EmptyChainException as AliasEmptyChainException
        from domprob.announcements.validation.chain import EmptyChainException
        # Act
        # Assert
        assert AliasEmptyChainException is EmptyChainException


class TestAnnouncementChainValidationExceptionImports:

    def test_invalid_link_exception(self):
        # Arrange
        from domprob.exceptions import InvalidLinkException as AliasInvalidLinkException
        from domprob.announcements.validation.chain_validation import InvalidLinkException
        # Act
        # Assert
        assert AliasInvalidLinkException is InvalidLinkException

    def test_link_exists_exception(self):
        # Arrange
        from domprob.exceptions import LinkExistsException as AliasLinkExistsException
        from domprob.announcements.validation.chain_validation import LinkExistsException
        # Act
        # Assert
        assert AliasLinkExistsException is LinkExistsException

    def test_validation_chain_exception(self):
        # Arrange
        from domprob.exceptions import ValidationChainException as AliasValidationChainException
        from domprob.announcements.validation.chain_validation import ValidationChainException
        # Act
        # Assert
        assert AliasValidationChainException is ValidationChainException
