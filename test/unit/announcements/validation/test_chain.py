from unittest.mock import MagicMock

import pytest
import re

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.base_validator import \
    BaseAnnouncementValidator
from domprob.announcements.validation.chain import (InvalidLinkException,
                                                    ValidationChainException,
                                                    EmptyChainException,
                                                    ValidationChain,
                                                    LinkTypeValidator,
                                                    UniqueLinkValidator,
                                                    LinkExistsException,
                                                    ABCLinkValidator,
                                                    LinkValidatorContext,
                                                    ABCLinkValidatorContext
)


class TestValidationChainException:

    def test_can_raise(self):
        with pytest.raises(ValidationChainException, match="Text exception"):
            raise ValidationChainException("Text exception")

    def test_inherits_from_announcement_exception(self):
        try:
            raise ValidationChainException()
        except AnnouncementException:
            assert True


@pytest.fixture
def mock_good_chain_link():
    class GoodChainLink(BaseAnnouncementValidator):
        next_ = None  # Define the required next_ attribute

        def validate(self, method: BoundAnnouncementMethod):
            super().validate(method)

    return GoodChainLink


@pytest.fixture
def mock_bad_chain_link():
    class BadChainLink:
        def validate(self, method: BoundAnnouncementMethod):
            pass

    return BadChainLink


class TestInvalidLinkException:

    def test_can_raise(self, mock_bad_chain_link, mock_good_chain_link):
        with pytest.raises(
            InvalidLinkException,
            match="Invalid link of type 'BadChainLink', expected type "
            "'GoodChainLink'",
        ):
            raise InvalidLinkException(
                mock_bad_chain_link(), mock_good_chain_link
            )

    def test_inherits_from_validation_chain_exception(
        self, mock_bad_chain_link, mock_good_chain_link
    ):
        try:
            raise InvalidLinkException(
                mock_bad_chain_link(), mock_good_chain_link
            )
        except ValidationChainException:
            assert True

    def test_attrs_set(self, mock_bad_chain_link, mock_good_chain_link):
        bad_chain_link = mock_bad_chain_link()
        try:
            raise InvalidLinkException(
                bad_chain_link, mock_good_chain_link
            )
        except InvalidLinkException as exc_info:
            assert exc_info.base == mock_good_chain_link
            assert exc_info.link == bad_chain_link


@pytest.fixture
def mock_chain():
    return ValidationChain(BaseAnnouncementValidator)


class TestEmptyChainException:

    def test_can_raise(self, mock_chain):
        with pytest.raises(
            EmptyChainException,
            match=re.escape("Nothing to validate, no links added to chain "
                  "'ValidationChain(base='BaseAnnouncementValidator')'"),
        ):
            raise EmptyChainException(mock_chain)

    def test_inherits_from_validation_chain_exception(
        self, mock_chain
    ):
        try:
            raise EmptyChainException(mock_chain)
        except ValidationChainException:
            assert True

    def test_attr_set(self, mock_chain):
        try:
            raise EmptyChainException(mock_chain)
        except EmptyChainException as exc_info:
            assert exc_info.chain == mock_chain


class TestLinkExistsException:
    def test_can_raise(self, mock_chain, mock_good_chain_link):
        link = mock_good_chain_link()
        with pytest.raises(
            LinkExistsException,
            match=re.escape(f"Link '{link!r}' already exists in chain '{mock_chain}'"),
        ):
            raise LinkExistsException(link, mock_chain)

    def test_inherits_from_validation_chain_exception(
        self, mock_chain, mock_good_chain_link
    ):
        link = mock_good_chain_link()
        try:
            raise LinkExistsException(link, mock_chain)
        except ValidationChainException:
            assert True

    def test_attrs_set(self, mock_chain, mock_good_chain_link):
        link = mock_good_chain_link()
        try:
            raise LinkExistsException(link, mock_chain)
        except LinkExistsException as exc_info:
            assert exc_info.link == link
            assert exc_info.chain == mock_chain


class TestABCLinkValidator:
    def test_abstract_method(self, mock_chain):
        class TestValidator(ABCLinkValidator):
            pass

        with pytest.raises(TypeError):
            TestValidator(mock_chain)

    def test_validate_invoked(self, mock_chain, mock_good_chain_link):
        class TestValidator(ABCLinkValidator):
            def validate(self, link):
                assert isinstance(link, mock_good_chain_link)

        validator = TestValidator(mock_chain)
        link = mock_good_chain_link()
        validator.validate(link)


# Test LinkTypeValidator
class TestLinkTypeValidator:
    def test_validate_valid_link(self, mock_chain, mock_good_chain_link):
        validator = LinkTypeValidator(mock_chain)
        link = mock_good_chain_link()
        validator.validate(link)  # Should not raise an exception

    def test_validate_invalid_link(self, mock_chain, mock_bad_chain_link):
        validator = LinkTypeValidator(mock_chain)
        link = mock_bad_chain_link()
        with pytest.raises(InvalidLinkException):
            validator.validate(link)


# Test UniqueLinkValidator
class TestUniqueLinkValidator:
    def test_validate_unique_link(self, mock_chain, mock_good_chain_link):
        validator = UniqueLinkValidator(mock_chain)
        link = mock_good_chain_link()
        validator.validate(link)  # Should not raise an exception

    def test_validate_duplicate_link(self, mock_chain, mock_good_chain_link):
        link = mock_good_chain_link()
        mock_chain.append(link)

        validator = UniqueLinkValidator(mock_chain)
        with pytest.raises(LinkExistsException):
            validator.validate(link)


class TestABCLinkValidatorContext:
    def test_abstract_methods(self, mock_chain):
        class TestContext(ABCLinkValidatorContext):
            pass

        with pytest.raises(TypeError):
            TestContext(mock_chain)

    def test_methods_invoked(self, mock_chain, mock_good_chain_link):
        class TestContext(ABCLinkValidatorContext):
            validator_num = 0
            def add_validators(self, *validators):
                self.validator_num += len(validators)

            def validate(self, link):
                assert isinstance(link, mock_good_chain_link)

        context = TestContext(mock_chain)
        link = mock_good_chain_link()
        context.validate(link)

        context.add_validators(LinkTypeValidator, UniqueLinkValidator)
        assert context.validator_num == 2


# Test LinkValidatorContext
class TestLinkValidatorContext:
    def test_default_validators(self, mock_chain, mock_good_chain_link):
        context = LinkValidatorContext(mock_chain)
        assert len(context.validators) > 0

        link = mock_good_chain_link()
        context.validate(link)  # Should not raise an exception

    def test_custom_validators(self, mock_chain, mock_good_chain_link):
        class CustomValidator(ABCLinkValidator):
            def validate(self, link):
                assert isinstance(link, mock_good_chain_link)

        context = LinkValidatorContext(mock_chain, CustomValidator)
        link = mock_good_chain_link()
        context.validate(link)

    def test_validate_multiple_links(self, mock_chain, mock_good_chain_link):
        context = LinkValidatorContext(mock_chain)
        links = [mock_good_chain_link() for _ in range(3)]
        context.validate(*links)  # Should not raise an exception


class TestValidationChain:
    @pytest.fixture
    def mock_chain(self):
        return ValidationChain(BaseAnnouncementValidator)

    @pytest.fixture
    def mock_good_chain_link(self):
        class GoodChainLink(BaseAnnouncementValidator):
            def validate(self, method: BoundAnnouncementMethod):
                super().validate(method)

        return GoodChainLink

    @pytest.fixture
    def mock_good_chain_link_instance(self, mock_good_chain_link):
        return mock_good_chain_link()

    @pytest.fixture
    def mock_good_chain_links(self, mock_good_chain_link):
        return [mock_good_chain_link() for _ in range(3)]

    def test_initialisation(self, mock_chain):
        assert isinstance(mock_chain, ValidationChain)
        assert len(mock_chain) == 0

    def test_append_valid_link(self, mock_chain, mock_good_chain_link_instance):
        mock_chain.append(mock_good_chain_link_instance)
        assert len(mock_chain) == 1
        assert mock_chain[0] == mock_good_chain_link_instance

    def test_append_invalid_link(self, mock_chain, mock_bad_chain_link):
        invalid_link = mock_bad_chain_link()
        with pytest.raises(
            InvalidLinkException,
            match=f"Invalid link of type '{type(invalid_link).__name__}', expected type 'BaseAnnouncementValidator'",
        ):
            mock_chain.append(invalid_link)

    def test_extend_with_valid_links(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        assert len(mock_chain) == len(mock_good_chain_links)
        for i, link in enumerate(mock_good_chain_links):
            assert mock_chain[i] == link

    def test_extend_with_invalid_links(self, mock_chain, mock_bad_chain_link):
        invalid_links = [mock_bad_chain_link(), mock_bad_chain_link()]
        with pytest.raises(InvalidLinkException):
            mock_chain.extend(invalid_links)

    def test_set_single_item(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        new_link = mock_good_chain_links[0]  # Change this to a new, unique instance
        unique_link = type(new_link)()  # Create a unique instance
        mock_chain[1] = unique_link
        assert mock_chain[1] == unique_link

    def test_set_slice_items(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        new_links = [type(link)() for link in mock_good_chain_links[:2]]  # Ensure uniqueness
        mock_chain[0:2] = new_links
        assert len(mock_chain) == len(mock_good_chain_links)
        assert mock_chain[:2] == new_links

    def test_remove_single_item(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        del mock_chain[1]
        assert len(mock_chain) == len(mock_good_chain_links) - 1
        assert mock_good_chain_links[1] not in mock_chain

    def test_remove_slice_items(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        del mock_chain[1:]
        assert len(mock_chain) == 1
        assert mock_chain[0] == mock_good_chain_links[0]

    def test_clear(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        mock_chain.clear()
        assert len(mock_chain) == 0

    def test_validate_chain_empty(self, mock_chain):
        with pytest.raises(
            EmptyChainException,
            match=re.escape(f"Nothing to validate, no links added to chain '{mock_chain!r}'"),
        ):
            mock_chain.validate_chain()

    def test_validate_chain(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        mock_method = MagicMock(spec=BoundAnnouncementMethod)  # Mock method
        try:
            mock_chain.validate_chain(mock_method)
        except ValidationChainException:
            pytest.fail("Unexpected exception raised during validation.")

    def test_contains(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        assert mock_good_chain_links[0] in mock_chain

        class ConcreteValidator(BaseAnnouncementValidator):
            def validate(self, method: BoundAnnouncementMethod):
                pass

        assert ConcreteValidator() not in mock_chain

    def test_repr(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        expected_repr = f"ValidationChain(base='BaseAnnouncementValidator')"
        assert repr(mock_chain) == expected_repr

    def test_str(self, mock_chain, mock_good_chain_links):
        mock_chain.extend(mock_good_chain_links)
        expected_str = " -> ".join(map(str, mock_good_chain_links))
        assert str(mock_chain) == expected_str
