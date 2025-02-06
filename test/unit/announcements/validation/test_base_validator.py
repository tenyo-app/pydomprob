import inspect
from collections import OrderedDict

import pytest

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.method import (
    BoundAnnouncementMethod,
    AnnouncementMethod,
)
from domprob.announcements.validation.base_validator import (
    BaseValidator,
    ValidatorException,
)


class MockValidationChainLink(BaseValidator):
    def validate(self, b_meth: BoundAnnouncementMethod) -> None:
        pass


class MockAnnouncementValidator(BaseValidator):
    def validate(self, b_meth: BoundAnnouncementMethod) -> None:
        if hasattr(b_meth, "validated"):
            b_meth.validated = True
        super().__init__()


class MockInstrument:
    pass


@pytest.fixture
def mock_bound_method():
    class Cls:
        def mock_method(self, instrument: MockInstrument) -> None:
            pass

    announce_meth = AnnouncementMethod(Cls.mock_method)
    sig = inspect.signature(Cls.mock_method)
    b_params = inspect.BoundArguments(sig, OrderedDict())
    # Bind the arguments correctly
    bound = sig.bind_partial(Cls())
    # Assign the correct args and kwargs
    b_params.arguments = bound.arguments
    b_meth = BoundAnnouncementMethod(announce_meth, b_params)
    setattr(b_meth, "validated", False)
    return b_meth


class TestValidatorException:
    def test_inherits_from_announcement_exception(self):
        # Arrange
        # Act + Assert
        with pytest.raises(AnnouncementException):
            raise ValidatorException("Validation failed")

    def test_matches_message(self):
        # Arrange
        # Act
        with pytest.raises(ValidatorException) as exc_info:
            raise ValidatorException("Validation failed")
        # Assert
        assert str(exc_info.value) == "Validation failed"


class TestBaseAnnouncementValidator:
    def test_is_abstract(self):
        # Arrange
        # Act + Assert
        with pytest.raises(TypeError) as exc_info:
            BaseValidator()
        # Assert
        msg_start = "Can't instantiate abstract class BaseValidator"
        assert str(exc_info.value).startswith(msg_start)

    def test_concrete_implementation_without_next(self):
        # Arrange + Act
        mock_validator = MockAnnouncementValidator()
        # Assert
        assert hasattr(mock_validator, "next_")
        assert mock_validator.next_ is None

    def test_concrete_implementation_with_next(self):
        # Arrange
        next_validator = MockAnnouncementValidator()
        mock_validator = MockAnnouncementValidator()
        # Act
        mock_validator.next_ = next_validator
        # Assert
        assert hasattr(mock_validator, "next_")
        assert mock_validator.next_ is next_validator

    def test_repr(self):
        # Arrange
        mock_validator = MockAnnouncementValidator()
        next_validator = MockAnnouncementValidator()
        mock_validator.next_ = next_validator
        # Act + Assert
        assert repr(next_validator) == "MockAnnouncementValidator(next_=None)"
        assert repr(mock_validator) == (
            f"MockAnnouncementValidator(next_={next_validator!r})"
        )

    def test_validate_calls_next(self, mock_bound_method):
        # Arrange
        next_validator = MockAnnouncementValidator()
        mock_validator = MockAnnouncementValidator()
        mock_validator.next_ = next_validator
        # Act
        mock_validator.validate(mock_bound_method)
        # Assert
        assert mock_bound_method.validated is True

    def test_validate_without_next(self, mock_bound_method):
        # Arrange
        mock_validator = MockAnnouncementValidator()
        # Act
        mock_validator.validate(mock_bound_method)
        # Assert
        assert mock_bound_method.validated is True
