class TestSensorExceptionImport:
    def test_sensor_exception(self):
        # Arrange
        from domprob.exceptions import (
            SensorException as AliasSensorException,
        )
        from domprob.sensors.exc import SensorException

        # Act
        # Assert
        assert AliasSensorException is SensorException


class TestSensorMethodExceptionImport:

    def test_partial_bind_exception(self):
        # Arrange
        from domprob.exceptions import (
            PartialBindException as AliasPartialBindException,
        )
        from domprob.sensors.meth_binder import PartialBindException

        # Act
        # Assert
        assert AliasPartialBindException is PartialBindException


class TestSensorValidationExceptionImports:

    def test_validater_exception(self):
        # Arrange
        from domprob.exceptions import (
            ValidatorException as AliasValidatorException,
        )
        from domprob.sensors.validate.vals import (
            ValidatorException,
        )

        # Act
        # Assert
        assert AliasValidatorException is ValidatorException

    def test_instrum_type_exception(self):
        # Arrange
        from domprob.exceptions import (
            InstrumTypeException as AliasInstrumTypeException,
        )
        from domprob.sensors.validate.vals import (
            InstrumTypeException,
        )

        # Act
        # Assert
        assert AliasInstrumTypeException is InstrumTypeException

    def test_missing_instrum_exception(self):
        # Arrange
        from domprob.exceptions import (
            MissingInstrumException as AliasMissingInstrumException,
        )
        from domprob.sensors.validate.vals import (
            MissingInstrumException,
        )

        # Act
        # Assert
        assert AliasMissingInstrumException is MissingInstrumException

    def test_no_supported_instrums_exception(self):
        # Arrange
        from domprob.exceptions import (
            NoSupportedInstrumsException as AliasNoSupportedInstrumsException,
        )
        from domprob.sensors.validate.vals import (
            NoSupportedInstrumsException,
        )

        # Act
        # Assert
        assert (
            AliasNoSupportedInstrumsException is NoSupportedInstrumsException
        )


class TestSensorChainExceptionImport:

    def test_empty_chain_exception(self):
        # Arrange
        from domprob.exceptions import (
            EmptyChainException as AliasEmptyChainException,
        )
        from domprob.sensors.validate.chain import EmptyChainException

        # Act
        # Assert
        assert AliasEmptyChainException is EmptyChainException


class TestSensorChainValidationExceptionImports:

    def test_invalid_link_exception(self):
        # Arrange
        from domprob.exceptions import (
            InvalidLinkException as AliasInvalidLinkException,
        )
        from domprob.sensors.validate.chain_val import (
            InvalidLinkException,
        )

        # Act
        # Assert
        assert AliasInvalidLinkException is InvalidLinkException

    def test_link_exists_exception(self):
        # Arrange
        from domprob.exceptions import (
            LinkExistsException as AliasLinkExistsException,
        )
        from domprob.sensors.validate.chain_val import (
            LinkExistsException,
        )

        # Act
        # Assert
        assert AliasLinkExistsException is LinkExistsException

    def test_validation_chain_exception(self):
        # Arrange
        from domprob.exceptions import (
            ValidationChainException as AliasValidationChainException,
        )
        from domprob.sensors.validate.chain_val import (
            ValidationChainException,
        )

        # Act
        # Assert
        assert AliasValidationChainException is ValidationChainException
