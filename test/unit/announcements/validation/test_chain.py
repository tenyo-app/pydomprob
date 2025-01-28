import copy
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
            validator.validate(link)

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

    def test_extend_with_no_links(self, mock_validator_chain):
        # Arrange
        links = []
        num_links = len(mock_validator_chain)
        # Act
        mock_validator_chain.extend(links)
        # Assert
        assert len(mock_validator_chain) == num_links

    def test_setitem_single_index(self, mock_validator_chain, mock_good_link):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        link3 = mock_good_link()
        mock_validator_chain.extend([link1, link2, link3])
        new_link = mock_good_link()
        # Act
        mock_validator_chain[1] = new_link  # Replace link2 with new_link
        # Assert
        assert len(mock_validator_chain) == 3
        assert mock_validator_chain[0] == link1
        assert mock_validator_chain[1] == new_link
        assert mock_validator_chain[2] == link3
        assert link1.next_ == new_link
        assert new_link.next_ == link3

    def test_setitem_slice(self, mock_validator_chain, mock_good_link):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        link3 = mock_good_link()
        link4 = mock_good_link()
        mock_validator_chain.extend([link1, link2, link3, link4])
        new_links = [mock_good_link(), mock_good_link()]
        # Act
        mock_validator_chain[1:3] = (
            new_links  # Replace link2 and link3 with new_links
        )
        # Assert
        assert len(mock_validator_chain) == 4
        assert mock_validator_chain[0] == link1
        assert mock_validator_chain[1] == new_links[0]
        assert mock_validator_chain[2] == new_links[1]
        assert mock_validator_chain[3] == link4
        assert link1.next_ == new_links[0]
        assert new_links[0].next_ == new_links[1]
        assert new_links[1].next_ == link4

    def test_setitem_negative_index(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        link3 = mock_good_link()
        mock_validator_chain.extend([link1, link2, link3])
        new_link = mock_good_link()
        # Assert
        mock_validator_chain[-1] = new_link  # Replace link3 with new_link
        # Assert
        assert len(mock_validator_chain) == 3
        assert mock_validator_chain[0] == link1
        assert mock_validator_chain[1] == link2
        assert mock_validator_chain[2] == new_link
        assert link2.next_ == new_link
        assert new_link.next_ is None

    def test_setitem_invalid_type(
        self, mock_validator_chain, mock_good_link, mock_bad_link
    ):
        # Arrange
        link1 = mock_good_link()
        mock_validator_chain.append(link1)
        # Act + Assert
        with pytest.raises(InvalidLinkException):
            mock_validator_chain[0] = mock_bad_link()  # Invalid type

    def test_setitem_iterable_to_single_index(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link1 = mock_good_link()
        mock_validator_chain.append(link1)
        # Act
        with pytest.raises(TypeError) as exc_info:
            mock_validator_chain[0] = [mock_good_link()]
        # Assert
        assert (
            str(exc_info.value)
            == "Cannot assign an iterable to a single index"
        )

    def test_setitem_slice_to_non_iterable(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        mock_validator_chain.extend([link1, link2])
        # Act
        with pytest.raises(TypeError) as exc_info:
            mock_validator_chain[0:2] = mock_good_link()
        # Assert
        assert (
            str(exc_info.value) == "Expected an iterable for slice assignment"
        )

    def test_setitem_single_invalid_index(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link1 = mock_good_link()
        mock_validator_chain.append(link1)
        new_link = mock_good_link()
        # Act
        with pytest.raises(TypeError) as exc_info:
            mock_validator_chain["invalid index"] = new_link
        # Assert
        assert str(exc_info.value) == "Invalid index type: str"

    def test_delete_single_item(self, mock_validator_chain, mock_good_link):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        link3 = mock_good_link()
        mock_validator_chain.extend([link1, link2, link3])
        # Act
        del mock_validator_chain[1]  # Delete the second link (link2)
        # Assert
        assert len(mock_validator_chain) == 2
        assert mock_validator_chain[0] == link1
        assert mock_validator_chain[1] == link3
        assert link1.next_ == link3  # next_ of link1 should now point to link3
        assert link3.next_ is None  # link3 is now the last link

    def test_delete_slice(self, mock_validator_chain, mock_good_link):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        link3 = mock_good_link()
        link4 = mock_good_link()
        mock_validator_chain.extend([link1, link2, link3, link4])
        # Act
        del mock_validator_chain[1:3]  # Delete link2 and link3
        # Assert
        assert len(mock_validator_chain) == 2
        assert mock_validator_chain[0] == link1
        assert mock_validator_chain[1] == link4
        assert link1.next_ == link4  # next_ of link1 should now point to link4
        assert link4.next_ is None  # link4 is now the last link

    def test_delete_first_item(self, mock_validator_chain, mock_good_link):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        mock_validator_chain.extend([link1, link2])
        # Act
        del mock_validator_chain[0]  # Delete the first link (link1)
        # Assert
        assert len(mock_validator_chain) == 1
        assert mock_validator_chain[0] == link2
        assert link2.next_ is None  # link2 is now the first and last link

    def test_delete_last_item(self, mock_validator_chain, mock_good_link):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        mock_validator_chain.extend([link1, link2])
        # Act
        del mock_validator_chain[1]  # Delete the last link (link2)
        # Assert
        assert len(mock_validator_chain) == 1
        assert mock_validator_chain[0] == link1
        assert link1.next_ is None  # link1 is now the last link

    def test_delete_negative_index(self, mock_validator_chain, mock_good_link):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        link3 = mock_good_link()
        mock_validator_chain.extend([link1, link2, link3])
        # Act
        del mock_validator_chain[-2]  # Delete the second-to-last link (link2)
        # Assert
        assert len(mock_validator_chain) == 2
        assert mock_validator_chain[0] == link1
        assert mock_validator_chain[1] == link3
        assert link1.next_ == link3  # next_ of link1 should now point to link3
        assert link3.next_ is None  # link3 is now the last link

    def test_delete_invalid_index(self, mock_validator_chain, mock_good_link):
        # Arrange
        link1 = mock_good_link()
        mock_validator_chain.append(link1)
        # Act + Assert
        with pytest.raises(IndexError):
            del mock_validator_chain[5]  # Out of range index
        with pytest.raises(TypeError):
            del mock_validator_chain["invalid"]  # Invalid index type

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

    def test_remove_wrong_index_type(
        self, mock_validator_chain, mock_good_chain_links
    ):
        # Arrange
        # Act
        with pytest.raises(TypeError) as exc_info:
            del mock_validator_chain["incorrect index type"]
        # Assert
        assert str(exc_info.value) == "Invalid index type: str"

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
        assert "string" not in mock_validator_chain

    def test_bool_false(self, mock_validator_chain):
        # Arrange
        # Act
        # Assert
        assert not mock_validator_chain

    def test_bool_true(self, mock_validator_chain, mock_good_link):
        # Arrange
        mock_validator_chain._links.append(mock_good_link)
        # Act
        # Assert
        assert mock_validator_chain

    def test_eq(self, mock_validator_chain, mock_good_link):
        # Arrange
        chain_1 = copy.deepcopy(mock_validator_chain)
        chain_2 = copy.deepcopy(mock_validator_chain)
        chain_3 = copy.deepcopy(mock_validator_chain)
        chain_3._links.append(mock_good_link)
        # Act
        # Assert
        assert "Incorrect eq type" != chain_1
        assert chain_1 == chain_2
        assert chain_1 != chain_3

    def test_insert_into_empty_chain(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link = mock_good_link()
        # Act
        mock_validator_chain.insert(0, link)
        # Assert
        assert len(mock_validator_chain) == 1
        assert mock_validator_chain[0] == link
        assert link.next_ is None

    def test_insert_at_start_of_chain(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        mock_validator_chain.append(link1)
        # Act
        mock_validator_chain.insert(0, link2)
        # Assert
        assert len(mock_validator_chain) == 2
        assert mock_validator_chain[0] == link2
        assert mock_validator_chain[1] == link1
        assert link2.next_ == link1

    def test_insert_at_end_of_chain(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        mock_validator_chain.append(link1)
        # Act
        mock_validator_chain.insert(len(mock_validator_chain), link2)
        # Assert
        assert len(mock_validator_chain) == 2
        assert mock_validator_chain[0] == link1
        assert mock_validator_chain[1] == link2
        assert link1.next_ == link2
        assert link2.next_ is None

    def test_insert_in_middle_of_chain(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        link3 = mock_good_link()
        mock_validator_chain.append(link1)
        mock_validator_chain.append(link3)
        # Act
        mock_validator_chain.insert(1, link2)
        # Assert
        assert len(mock_validator_chain) == 3
        assert mock_validator_chain[0] == link1
        assert mock_validator_chain[1] == link2
        assert mock_validator_chain[2] == link3
        assert link1.next_ == link2
        assert link2.next_ == link3

    def test_insert_invalid_link(self, mock_validator_chain, mock_bad_link):
        # Arrange
        link1 = mock_bad_link()
        # Act + Assert
        with pytest.raises(InvalidLinkException):
            mock_validator_chain.insert(0, link1)

    def test_insert_duplicate_link(self, mock_validator_chain, mock_good_link):
        # Arrange
        link = mock_good_link()
        mock_validator_chain.append(link)
        # Act + Assert
        with pytest.raises(LinkExistsException):
            mock_validator_chain.insert(1, link)

    def test_insert_with_negative_index(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        mock_validator_chain.append(link1)
        # Act
        mock_validator_chain.insert(-1, link2)
        # Assert
        assert len(mock_validator_chain) == 2
        assert mock_validator_chain[0] == link2
        assert mock_validator_chain[1] == link1
        assert link2.next_ == link1

    def test_iter_empty_chain(self, mock_validator_chain):
        # Arrange
        # Act
        result = list(mock_validator_chain)
        # Assert
        assert result == []

    def test_iter_single_element(self, mock_validator_chain, mock_good_link):
        # Arrange
        link = mock_good_link()
        mock_validator_chain.append(link)
        # Act
        result = list(mock_validator_chain)
        # Assert
        assert result == [link]

    def test_iter_multiple_elements(
        self, mock_validator_chain, mock_good_link
    ):
        # Arrange
        link1 = mock_good_link()
        link2 = mock_good_link()
        link3 = mock_good_link()
        mock_validator_chain.extend([link1, link2, link3])
        # Act
        result = list(mock_validator_chain)
        # Assert
        assert result == [link1, link2, link3]

    def test_iter_returns_generator(self, mock_validator_chain):
        # Arrange
        # Act
        result = mock_validator_chain.__iter__()
        # Assert
        assert hasattr(result, "__iter__")  # Confirm it’s iterable
        assert hasattr(result, "__next__")  # Confirm it’s an iterator

    def test_repr(self, mock_validator_chain, mock_good_chain_links):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        # Act
        mock_chain_repr = repr(mock_validator_chain)
        # Assert
        expected_repr = f"ValidationChain(base='BaseValidator')"
        assert mock_chain_repr == expected_repr

    def test_str(self, mock_validator_chain, mock_good_chain_links):
        # Arrange
        mock_validator_chain.extend(mock_good_chain_links)
        expected_str = " -> ".join(map(str, mock_good_chain_links))
        # Act
        mock_chain_str = str(mock_validator_chain)
        # Assert
        assert mock_chain_str == expected_str
