import pytest

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.base_validator import BaseValidator
from domprob.announcements.validation.chain import (
    ABCLinkValidator,
    ABCLinkValidatorContext,
    EmptyChainException,
    LinkValidatorContext,
    ValidationChain,
)
from domprob.announcements.validation.chain_validation import (
    InvalidLinkException,
    LinkExistsException,
    LinkTypeValidator,
    UniqueLinkValidator,
    ValidationChainException,
)


@pytest.fixture
def mock_good_link():
    class GoodChainLink(BaseValidator):
        next_ = None  # Define the required next_ attribute

        def validate(self, method: BoundAnnouncementMethod):
            super().validate(method)

    return GoodChainLink


@pytest.fixture
def mock_good_chain_links(mock_good_link):
    return [mock_good_link() for _ in range(3)]


@pytest.fixture
def mock_bad_link():
    class BadChainLink:
        def validate(self, method: BoundAnnouncementMethod):
            pass

    return BadChainLink


@pytest.fixture
def mock_validator_chain():
    return ValidationChain(BaseValidator)


class TestValidationChainException:
    def test_can_raise(self):
        # Arrange
        # Act
        with pytest.raises(ValidationChainException) as exc_info:
            raise ValidationChainException("Text exception")
        # Assert
        assert str(exc_info.value) == "Text exception"

    def test_inherits_from_announcement_exception(self):
        # Arrange
        # Act + Assert
        with pytest.raises(AnnouncementException):
            raise ValidationChainException("Text exception")


class TestInvalidLinkException:
    def test_can_raise(self, mock_bad_link, mock_good_link):
        # Arrange
        # Act
        with pytest.raises(InvalidLinkException) as exc_info:
            raise InvalidLinkException(mock_bad_link(), mock_good_link)
        # Assert
        assert (
            str(exc_info.value)
            == "Invalid link of type 'BadChainLink', expected type "
            "'GoodChainLink'"
        )

    def test_inherits_from_validation_chain_exception(
        self, mock_bad_link, mock_good_link
    ):
        # Arrange
        # Act + Assert
        with pytest.raises(ValidationChainException):
            raise InvalidLinkException(mock_bad_link(), mock_good_link)

    def test_attrs_set(self, mock_bad_link, mock_good_link):
        # Arrange
        bad_chain_link = mock_bad_link()
        # Act
        try:
            raise InvalidLinkException(bad_chain_link, mock_good_link)
        # Assert
        except InvalidLinkException as exc_info:
            assert exc_info.expected_type == mock_good_link
            assert exc_info.link == bad_chain_link


class TestEmptyChainException:

    def test_can_raise(self, mock_validator_chain):
        # Arrange
        # Act
        with pytest.raises(EmptyChainException) as exc_info:
            raise EmptyChainException(mock_validator_chain)
        # Assert
        assert (
            str(exc_info.value)
            == "Nothing to validate, no links added to chain "
            "'ValidationChain(base='BaseValidator')'"
        )

    def test_inherits_from_validation_chain_exception(
        self, mock_validator_chain
    ):
        # Arrange
        # Act + Assert
        with pytest.raises(ValidationChainException):
            raise EmptyChainException(mock_validator_chain)

    def test_attr_set(self, mock_validator_chain):
        # Arrange
        # Act
        try:
            raise EmptyChainException(mock_validator_chain)
        # Assert
        except EmptyChainException as exc_info:
            assert exc_info.chain == mock_validator_chain


class TestLinkExistsException:
    def test_can_raise(self, mock_validator_chain, mock_good_link):
        # Arrange
        link = mock_good_link()
        # Act
        with pytest.raises(LinkExistsException) as exc_info:
            raise LinkExistsException(link, mock_validator_chain)
        # Assert
        assert (
            str(exc_info.value) == f"Link '{link!r}' already exists in chain '"
            f"{mock_validator_chain!r}'"
        )

    def test_inherits_from_validation_chain_exception(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link = mock_good_link()
        # Act + Assert
        with pytest.raises(ValidationChainException):
            raise LinkExistsException(link, mock_validator_chain)

    def test_attrs_set(self, mock_validator_chain, mock_good_link):
        # Arrange
        link = mock_good_link()
        # Act
        try:
            raise LinkExistsException(link, mock_validator_chain)
        # Assert
        except LinkExistsException as exc_info:
            assert exc_info.link == link
            assert exc_info.chain == mock_validator_chain


class TestABCLinkValidator:
    def test_abstract_method(self, mock_validator_chain):
        # Arrange
        class TestValidator(ABCLinkValidator):
            pass

        # Act + Assert
        with pytest.raises(TypeError):
            TestValidator(mock_validator_chain)

    def test_validate_invoked(self, mock_validator_chain, mock_good_link):
        # Arrange
        class TestValidator(ABCLinkValidator):
            def validate(self, link):
                assert isinstance(link, mock_good_link)

        validator = TestValidator(mock_validator_chain)
        link = mock_good_link()
        # Act
        validator.validate(link)
        # Assert
        assert True


class TestLinkTypeValidator:
    def test_validate_valid_link(self, mock_validator_chain, mock_good_link):
        # Arrange
        validator = LinkTypeValidator(mock_validator_chain)
        link = mock_good_link()
        # Act
        validator.validate(link)  # Should not raise an exception
        # Assert
        assert True

    def test_validate_invalid_link(self, mock_validator_chain, mock_bad_link):
        # Arrange
        validator = LinkTypeValidator(mock_validator_chain)
        link = mock_bad_link()
        # Act + Assert
        with pytest.raises(InvalidLinkException):
            validator.validate(link)  # type: ignore

    def test_repr(self, mock_validator_chain, mock_good_link):
        # Arrange
        link = mock_good_link()
        mock_validator_chain.append(link)
        validator = LinkTypeValidator(mock_validator_chain)
        # Act
        validator_repr = repr(validator)
        # Assert
        exp = "LinkTypeValidator(ValidationChain(base='BaseValidator'))"
        assert validator_repr == exp


class TestUniqueLinkValidator:
    def test_validate_unique_link(self, mock_validator_chain, mock_good_link):
        # Arrange
        validator = UniqueLinkValidator(mock_validator_chain)
        link = mock_good_link()
        # Act
        validator.validate(link)  # Should not raise an exception
        # Assert
        assert True

    def test_validate_duplicate_link(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link = mock_good_link()
        mock_validator_chain.append(link)
        validator = UniqueLinkValidator(mock_validator_chain)
        # Act + Assert
        with pytest.raises(LinkExistsException):
            validator.validate(link)

    def test_repr(self, mock_validator_chain, mock_good_link):
        # Arrange
        link = mock_good_link()
        mock_validator_chain.append(link)
        validator = UniqueLinkValidator(mock_validator_chain)
        # Act
        validator_repr = repr(validator)
        # Assert
        exp = "UniqueLinkValidator(ValidationChain(base='BaseValidator'))"
        assert validator_repr == exp


class TestABCLinkValidatorContext:
    def test_abstract_methods(self, mock_validator_chain):
        # Arrange
        class TestContext(ABCLinkValidatorContext):
            pass

        # Act + Assert
        with pytest.raises(TypeError):
            TestContext(mock_validator_chain)

    def test_methods_invoked(self, mock_validator_chain, mock_good_link):
        # Arrange
        class TestContext(ABCLinkValidatorContext):
            validator_num = 0
            validated = False

            def add_validators(self, *validators):
                self.validator_num += len(validators)

            def validate(self, link):
                self.validated = True

        context = TestContext(mock_validator_chain)
        link = mock_good_link()
        # Act
        context.validate(link)
        context.add_validators(LinkTypeValidator, UniqueLinkValidator)
        # Assert
        assert context.validated
        assert context.validator_num == 2

    def test_repr(self, mock_validator_chain, mock_good_chain_links):
        # Arrange
        class TestContext(ABCLinkValidatorContext):
            def add_validators(self, *validators): ...
            def validate(self, link): ...

        context = TestContext(mock_validator_chain)
        # Act
        context_repr = repr(context)
        # Assert
        assert (
            context_repr
            == f"TestContext(chain=ValidationChain(base='BaseValidator'))"
        )


class TestLinkValidatorContext:
    def test_default_validators(self, mock_validator_chain, mock_good_link):
        # Arrange
        context = LinkValidatorContext(mock_validator_chain)
        link = mock_good_link()
        # Act
        context.validate(link)  # Should not raise an exception
        # Assert
        assert len(context.validators) == 2

    def test_custom_validators(self, mock_validator_chain, mock_good_link):
        # Arrange
        class CustomValidator(ABCLinkValidator):
            def validate(self, link):
                assert isinstance(link, mock_good_link)

        context = LinkValidatorContext(mock_validator_chain, CustomValidator)
        link = mock_good_link()
        # Act
        context.validate(link)  # Should not raise an exception
        # Assert
        assert True

    def test_validate_multiple_links(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        context = LinkValidatorContext(mock_validator_chain)
        links = [mock_good_link() for _ in range(3)]
        # Act
        context.validate(*links)  # Should not raise an exception
        # Assert

    def test_repr(self, mock_validator_chain):
        # Arrange
        context = LinkValidatorContext(mock_validator_chain)
        # Act
        context_repr = repr(context)
        # Assert
        exp = f"LinkValidatorContext(ValidationChain(base='BaseValidator'))"
        assert context_repr == exp
