import json

import pytest

from domprob.obs.obs_attrs.base_obs_attr import BaseObsAttr


@pytest.fixture
def first_attr_cls():
    class FirstAttr(BaseObsAttr):
        NAME: str = 'first'

        def __call__(self):
            return "FirstAttr"

    return FirstAttr


@pytest.fixture
def second_attr_cls(first_attr_cls):
    class SecondAttribute(BaseObsAttr):

        def __call__(self):
            return "SecondAttr"

    return SecondAttribute


@pytest.fixture
def third_attr_cls(first_attr_cls, second_attr_cls):
    class ThirdAttr(BaseObsAttr):
        NAME: str = 'third_attribute'
        @property
        def children(self) -> tuple[BaseObsAttr, ...]:
            return first_attr_cls(), second_attr_cls()

    return ThirdAttr

@pytest.fixture
def fourth_attr_cls(third_attr_cls):
    class FourthAttr(BaseObsAttr):
        NAME: str = 'fourth_attribute'
        @property
        def children(self) -> tuple[BaseObsAttr, ...]:
            return third_attr_cls(),

    return FourthAttr


class TestBaseObsAttr:
    def test_cls_attributes(self, first_attr_cls):
        # Arrange
        # Act
        # Assert
        assert first_attr_cls.NAME == 'first'

    def test_init(self, first_attr_cls):
        # Arrange
        # Act
        attr = first_attr_cls()
        # Assert
        assert attr._name is None

    def test_call(self, third_attr_cls):
        # Arrange
        # Act
        attr = third_attr_cls()
        # Assert
        assert attr() is None

    def test_children_property(self, first_attr_cls, second_attr_cls, third_attr_cls):
        # Arrange
        third_attr = third_attr_cls()
        # Act
        children = third_attr.children
        # Assert
        assert len(children) == 2
        assert type(children[0]) == first_attr_cls
        assert type(children[1]) == second_attr_cls

    def test_name_property_cls_attr_implemented(self, first_attr_cls):
        # Arrange
        attr = first_attr_cls()
        # Act
        name = attr.name
        # Assert
        assert name == first_attr_cls.NAME
        assert name == attr.NAME

    def test_name_property_cls_attr_not_implemented(self, second_attr_cls):
        # Arrange
        another_attr = second_attr_cls()
        # Act
        name = another_attr.name
        # Assert
        assert name == 'second'

    def test_name_property_caches_cls_attr_implemented(self, first_attr_cls):
        attr = first_attr_cls()
        # Act
        cache_before = attr._name
        _ = attr.name
        cache_after = attr._name
        _ = attr.name
        attr.NAME = 'not used'
        cache_after_again = attr._name
        # Assert
        assert cache_before is None
        assert attr.NAME != 'an_attr'
        assert cache_after == cache_after_again

    def test_calc_name(self, first_attr_cls, second_attr_cls):
        # Arrange
        first_attr_cls.NAME = None
        # Act
        first_attr_name = first_attr_cls().name
        second_attr_name = second_attr_cls().name
        # Assert
        assert first_attr_name == 'first'
        assert second_attr_name == 'second'

    def test_to_nested_json(self, fourth_attr_cls):
        # Arrange
        fourth_attr = fourth_attr_cls()
        # Act
        json_ = fourth_attr.to_nested_json()
        # Assert
        assert json_ == {
            'fourth_attribute': {
                'third_attribute': {
                    'first': 'FirstAttr',
                    'second': 'SecondAttr'
                }
            }
        }

    def test_to_flat_json(self, fourth_attr_cls):
        # Arrange
        fourth_attr = fourth_attr_cls()
        # Act
        json_ = fourth_attr.to_flat_json()
        # Assert
        assert json_ == {
            'fourth_attribute.third_attribute.first': 'FirstAttr',
            'fourth_attribute.third_attribute.second': 'SecondAttr',
        }

    def test_to_json_flat_default(self, fourth_attr_cls):
        # Arrange
        fourth_attr = fourth_attr_cls()
        # Act
        json_ = fourth_attr.to_json()
        # Assert
        assert json_ == {
            'fourth_attribute.third_attribute.first': 'FirstAttr',
            'fourth_attribute.third_attribute.second': 'SecondAttr',
        }

    def test_to_json_flat_true(self, fourth_attr_cls):
        # Arrange
        fourth_attr = fourth_attr_cls()
        # Act
        json_ = fourth_attr.to_json(flatten=True)
        # Assert
        assert json_ == {
            'fourth_attribute.third_attribute.first': 'FirstAttr',
            'fourth_attribute.third_attribute.second': 'SecondAttr',
        }

    def test_to_json_flat_false(self, fourth_attr_cls):
        # Arrange
        fourth_attr = fourth_attr_cls()
        # Act
        json_ = fourth_attr.to_json(flatten=False)
        # Assert
        assert json_ == {
            'fourth_attribute': {
                'third_attribute': {
                    'first': 'FirstAttr',
                    'second': 'SecondAttr'
                }
            }
        }

    def test_repr(self, first_attr_cls):
        # Arrange
        first_attr = first_attr_cls()
        # Act
        attr_repr = repr(first_attr)
        # Assert
        assert attr_repr == 'FirstAttr()'
