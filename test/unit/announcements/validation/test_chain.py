from unittest.mock import MagicMock

import pytest

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.base_validator import BaseValidator
from domprob.announcements.validation.chain import (
    ABCLinkValidator,
    ABCLinkValidatorContext,
    EmptyChainException,
    InvalidLinkException,
    LinkExistsException,
    LinkTypeValidator,
    LinkValidatorContext,
    UniqueLinkValidator,
    ValidationChain,
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
            assert exc_info.base == mock_good_link
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
            validator.validate(link)


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


class TestValidationChain:

    @pytest.fixture
    def mock_chain(self):
        return ValidationChain(BaseValidator)

    def test_initialisation(self, mock_validator_chain):
        # Arrange
        # Act
        # Assert
        assert isinstance(mock_validator_chain, ValidationChain)
        assert len(mock_validator_chain) == 0

    def test_append_valid_link(self, mock_validator_chain, mock_good_link):
        # Arrange
        link = mock_good_link()
        # Act
        mock_validator_chain.append(link)
        # Assert
        assert len(mock_validator_chain) == 1
        assert mock_validator_chain[0] == link

    def test_append_invalid_link(self, mock_validator_chain, mock_bad_link):
        # Arrange
        invalid_link = mock_bad_link()
        # Act
        with pytest.raises(InvalidLinkException) as exc_info:
            mock_validator_chain.append(invalid_link)
        # Assert
        assert (
            str(exc_info.value)
            == f"Invalid link of type '{type(invalid_link).__name__}', "
            f"expected type 'BaseValidator'"
        )

    def test_extend_with_valid_links(
        self, mock_validator_chain, mock_good_chain_links
    ):
        # Arrange
        # Act
        mock_validator_chain.extend(mock_good_chain_links)
        # Assert
        assert len(mock_validator_chain) == len(mock_good_chain_links)
        for i, link in enumerate(mock_good_chain_links):
            assert mock_validator_chain[i] == link

    def test_extend_with_invalid_links(
        self, mock_validator_chain, mock_bad_link
    ):
        # Arrange
        invalid_links = [mock_bad_link(), mock_bad_link()]
        # Act + Assert
        with pytest.raises(InvalidLinkException):
            mock_validator_chain.extend(invalid_links)

    def test_set_single_item(
        self, mock_validator_chain, mock_good_chain_links, mock_good_link
    ):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        link = mock_good_link()
        # Act
        mock_validator_chain[1] = link
        # Assert
        assert mock_validator_chain[1] == link

    def test_set_slice_items(
        self, mock_validator_chain, mock_good_chain_links, mock_good_link
    ):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        new_links = [mock_good_link() for _ in range(3)]  # Ensure uniqueness
        # Act
        mock_validator_chain[0:3] = new_links
        # Assert
        assert len(mock_validator_chain) == len(mock_good_chain_links)
        assert mock_validator_chain[:3] == new_links

    def test_remove_single_item(
        self, mock_validator_chain, mock_good_chain_links
    ):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        # Act
        del mock_validator_chain[1]
        # Assert
        assert len(mock_validator_chain) == len(mock_good_chain_links) - 1
        assert mock_good_chain_links[1] not in mock_validator_chain

    def test_remove_slice_items(
        self, mock_validator_chain, mock_good_chain_links
    ):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        # Act
        del mock_validator_chain[1:]
        # Assert
        assert len(mock_validator_chain) == 1
        assert mock_validator_chain[0] == mock_good_chain_links[0]

    def test_clear(self, mock_validator_chain, mock_good_chain_links):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        # Act
        mock_validator_chain.clear()
        # Assert
        assert len(mock_validator_chain) == 0

    def test_validate_chain_empty(self, mock_validator_chain):
        # Arrange
        # Act
        with pytest.raises(EmptyChainException) as exc_info:
            mock_validator_chain.validate_chain()
        # Assert
        assert (
            str(exc_info.value)
            == f"Nothing to validate, no links added to chain "
            f"'{mock_validator_chain!r}'"
        )

    def test_validate_chain(self, mock_validator_chain, mock_good_chain_links):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        mock_method = MagicMock(spec=BoundAnnouncementMethod)  # Mock method
        # Act
        try:
            mock_validator_chain.validate_chain(mock_method)
        # Assert
        except ValidationChainException:
            pytest.fail("Unexpected exception raised during validation.")

    def test_contains(self, mock_validator_chain, mock_good_chain_links):
        # Arrange
        class ConcreteValidator(BaseValidator):
            def validate(self, method: BoundAnnouncementMethod):
                pass

        mock_validator_chain.extend(mock_good_chain_links)
        # Act
        # Assert
        assert mock_good_chain_links[0] in mock_validator_chain
        assert ConcreteValidator() not in mock_validator_chain

    def test_repr(self, mock_validator_chain, mock_good_chain_links):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        expected_repr = f"ValidationChain(base='BaseValidator')"
        # Act
        mock_chain_repr = repr(mock_validator_chain)
        # Assert
        assert mock_chain_repr == expected_repr

    def test_str(self, mock_validator_chain, mock_good_chain_links):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        expected_str = " -> ".join(map(str, mock_good_chain_links))
        # Act
        mock_chain_str = str(mock_validator_chain)
        # Assert
        assert mock_chain_str == expected_str
