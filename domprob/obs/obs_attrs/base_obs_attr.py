from __future__ import annotations
import re
from abc import ABC
from typing import Any


class BaseObsAttr(ABC):
    """Base class for all observable attributes.

    This class provides a structure for defining hierarchical
    observable attributes that can be serialized to JSON in both
    nested and flattened formats.

    Attributes:
        NAME (str | None): Optional class-level name override.
    """

    NAME: str | None = None

    def __init__(self) -> None:
        self._name: str | None = None

    def __call__(self) -> Any | None:
        """Invokes the attribute.

        Returns:
            Any | None: The JSON serializable value of the attribute
                when called.

        Example:
            >>> from domprob.obs.obs_attrs.base_obs_attr import BaseObsAttr
            >>>
            >>> class MyAttr(BaseObsAttr):
            ...     def __call__(self):
            ...         return "Value"
            >>> attr = MyAttr()
            >>> attr()
            'Value'
        """
        return None

    @property
    def children(self) -> tuple[BaseObsAttr, ...]:
        """Gets the child attributes of this attribute.

        Returns:
            tuple[BaseObsAttr, ...]: A tuple containing child
                attributes.

        Example:
            >>> from domprob.obs.obs_attrs.base_obs_attr import BaseObsAttr
            >>>
            >>> class ParentAttr(BaseObsAttr):
            ...     @property
            ...     def children(self):
            ...         return (ChildAttr(),)
            ...
            >>> class ChildAttr(BaseObsAttr):
            ...     pass
            ...
            >>> parent = ParentAttr()
            >>> len(parent.children)
            1
        """
        return tuple()

    @property
    def name(self) -> str:
        """Gets the name of the attribute.

        If `NAME` is defined at the class level, it is used.
        Otherwise, the name is derived from the class name.

        Returns:
            str: The resolved name of the attribute.

        Example:
            >>> from domprob.obs.obs_attrs.base_obs_attr import BaseObsAttr
            >>>
            >>> class MyAttr(BaseObsAttr):
            ...     NAME = "custom_name"
            ...
            >>> class DefaultAttr(BaseObsAttr):
            ...     pass
            ...
            >>> MyAttr().name
            'custom_name'
            >>> DefaultAttr().name
            'default'
        """
        if self._name is None:
            if self.NAME is None:
                self._name = self._calc_name()
            else:
                self._name = self.NAME
        return self._name

    def _calc_name(self):
        """Calculates the attribute name from the class name.

        This method removes common suffixes like "Attr" and "Attribute"
        and converts CamelCase to snake_case.

        Returns:
            str: The computed name of the attribute.

        Example:
            >>> from domprob.obs.obs_attrs.base_obs_attr import BaseObsAttr
            >>>
            >>> class ExampleAttribute(BaseObsAttr):
            ...     pass
            ...
            >>> ExampleAttribute()._calc_name()
            'example'
        """
        name = self.__class__.__name__
        name = name.removesuffix("Attr").removesuffix("Attribute")
        name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return name

    def to_nested_json(self) -> dict[str, Any]:
        """Converts the attribute and its children into a nested JSON
        structure.

        The output is a dictionary where child attributes are nested
        under their parent.

        Returns:
            dict[str, Any]: The nested dictionary representation.

        Example:
            >>> from domprob.obs.obs_attrs.base_obs_attr import BaseObsAttr
            >>>
            >>> class ParentAttr(BaseObsAttr):
            ...     @property
            ...     def children(self):
            ...         return (ChildAttr(),)
            ...
            >>> class ChildAttr(BaseObsAttr):
            ...     def __call__(self):
            ...         return "child_value"
            ...
            >>> ParentAttr().to_nested_json()
            {'parent': {'child': 'child_value'}}
        """
        if not self.children:
            return {self.name: self()}
        nested_dict: dict[str, Any] = {self.name: {}}
        for child in self.children:
            nested_dict[self.name].update(child.to_nested_json())
        return nested_dict

    def to_flat_json(self, prefix: str = "") -> dict[str, Any]:
        """Converts the attribute and its children into a flattened
        JSON structure.

        The output is a dictionary where nested attributes are
        represented using dot-separated keys.

        Args:
            prefix (str, optional): Prefix for nested keys. Defaults to
            ''.

        Returns:
            dict[str, Any]: The flattened dictionary representation.

        Example:
            >>> from domprob.obs.obs_attrs.base_obs_attr import BaseObsAttr
            >>>
            >>> class ParentAttr(BaseObsAttr):
            ...     @property
            ...     def children(self):
            ...         return ChildAttr(),
            ...
            >>> class ChildAttr(BaseObsAttr):
            ...     def __call__(self):
            ...         return "child_value"
            ...
            >>> ParentAttr().to_flat_json()
            {'parent.child': 'child_value'}
        """
        if not self.children:
            return {prefix or self.name: self()}
        flat_dict: dict[str, Any] = {}
        for child in self.children:
            key = f"{prefix or self.name}.{child.name}"
            flat_dict.update(child.to_flat_json(prefix=key))
        return flat_dict

    def to_json(self, flatten: bool = True) -> Any:
        """Serializes the attribute and its children into JSON format.

        Args:
            flatten (bool, optional): If `True`, uses a flattened
                structure; otherwise, uses a nested structure. Defaults
                to `True`.

        Returns:
            Any: A dictionary representation of the attribute.

        Example:
            >>> from domprob.obs.obs_attrs.base_obs_attr import BaseObsAttr
            >>>
            >>> class ParentAttr(BaseObsAttr):
            ...     @property
            ...     def children(self):
            ...         return ChildAttr(),
            ...
            >>> class ChildAttr(BaseObsAttr):
            ...     def __call__(self):
            ...         return "child_value"
            ...
            >>> ParentAttr().to_json(flatten=True)
            {'parent.child': 'child_value'}
            >>> ParentAttr().to_json(flatten=False)
            {'parent': {'child': 'child_value'}}
        """
        if flatten:
            return self.to_flat_json()
        return self.to_nested_json()

    def __repr__(self) -> str:
        """Gets a string representation of the attribute.

        Returns:
            str: A string representing the attribute.

        Example:
            >>> from domprob.obs.obs_attrs.base_obs_attr import BaseObsAttr
            >>>
            >>> class ExampleAttr(BaseObsAttr):
            ...     pass
            ...
            >>> repr(ExampleAttr())
            'ExampleAttr()'
        """
        return f"{self.__class__.__name__}()"
