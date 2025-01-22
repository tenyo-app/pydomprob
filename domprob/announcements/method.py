import inspect
from collections.abc import Callable
from typing import Any, Generic, ParamSpec, TypeAlias, TypeVar

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.instruments import Instruments

_PMeth = ParamSpec("_PMeth")
_RMeth = TypeVar("_RMeth")
_WrappedMeth: TypeAlias = Callable[_PMeth, _RMeth]


class AnnouncementMethod:
    """Represents a decorated method with associated metadata.

    This class acts as a wrapper and provides an interface to interact
    with the supported instruments of a method decorated with
    `@announcements`. It also facilitates partially binding runtime
    arguments to the method before method execution.

    Args:
        meth (`Callable[P, R]`): The decorated method to be
            managed.

    Examples:
        >>> # Define a class with a decorated method
        >>> class Foo:
        ...     @announcement(BaseInstrument)
        ...     def bar(self, instrument):
        ...         pass
        ...
        >>> # Create an AnnoMethod instance
        >>> bar_method = AnnouncementMethod(Foo.bar)
        >>>
        >>> bar_method
        AnnoMethod(method=<function Foo.bar at ...>)
    """

    def __init__(self, meth: _WrappedMeth) -> None:
        self._meth = meth  # Explicitly declare type for mypy
        self._instruments = Instruments.from_method(self._meth)

    @property
    def method(self) -> _WrappedMeth:
        """The decorated method being managed.

        Returns:
            `Callable[P, R]`: The method.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         pass
            ...
            >>> # Create an AnnoMethod instance
            >>> bar_method = AnnouncementMethod(Foo.bar)
            >>>
            >>> bar_method.method
            <function Foo.bar at ...>
        """
        return self._meth

    @property
    def instruments(self):
        """The supported instrument classes associated with the
        decorated method.

        Returns:
            Instruments: The `Instruments` instance linked to the
                method.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         pass
            ...
            >>> # Create an AnnoMethod instance
            >>> bar_method = AnnouncementMethod(Foo.bar)
            >>>
            >>> bar_method.instruments
            Instruments(metadata=AnnoMetadata(method=Foo.bar))
            >>> list[bar_method.instruments]
            [BaseInstrument, BaseInstrument]
        """
        return self._instruments

    @property
    def signature(self) -> inspect.Signature:
        """The signature of the decorated method.

        Returns:
            inspect.Signature: The signature of the method.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         pass
            ...
            >>> # Create an AnnoMethod instance
            >>> bar_method = AnnouncementMethod(Foo.bar)
            >>>
            >>> bar_method.signature
            <Signature (self, instrument)>
        """
        return inspect.signature(self.method)

    def bind(
        self, *args: _PMeth.args, **kwargs: _PMeth.kwargs
    ) -> "BoundAnnouncementMethod":
        """Binds passed parameters to the method, returning a
        partially bound version.

        Args:
            *args (`P.args`): Positional arguments to bind to the
                method.
            **kwargs (`P.kwargs`): Keyword arguments to bind to the
                method.

        Returns:
            InstrumentBoundAnnoMethod: A new wrapper representing a
                partially bound method.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         pass
            ...
            >>> # Create an AnnoMethod instance
            >>> bar_method = AnnouncementMethod(Foo.bar)
            >>>
            >>> # Binds method with instrument instance
            >>> bound_method = bar_method.bind(BaseInstrument())
            >>> bound_method
            InstrumentBoundAnnoMethod(method=<function Foo.bar at ...>)
        """
        return BoundAnnouncementMethod(self.method, *args, **kwargs)

    def __repr__(self) -> str:
        """Returns a string representation of the `AnnoMethod`
        instance.

        Returns:
            str: The string representation of the instance.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         pass
            ...
            >>> # Create an AnnoMethod instance
            >>> bar_method = AnnouncementMethod(Foo.bar)
            >>>
            >>> repr(bar_method)
            "AnnoMethod(method=<function Foo.bar at ...>)"
        """
        return f"{self.__class__.__name__}(method={self.method!r})"


_BindExc: TypeAlias = "PartialBindException"


class PartialBindException(AnnouncementException):
    """Exception raised when binding arguments to a method's signature
    fails.

    This exception is used to handle errors that occur during partial
    argument binding, including missing required parameters.
    """

    @classmethod
    def general(cls, meth: AnnouncementMethod, e: Exception) -> _BindExc:
        """Creates a `PartialBindException` for a general binding
        error.

        Args:
            meth (`Callable[P, R]`): The method for which binding
                failed.
            e (`Exception`): The underlying exception that caused
                the failure.

        Returns:
            PartialBindException: The exception instance with the
                generated error message.

        Examples:
        >>> # Define a class with a method to decorate
        >>> class Foo:
        ...     def bar(self, instrument):
        ...         pass
        ...
        >>> from inspect import signature
        >>> sig = signature(Foo.bar)
        >>> try:
        ...     sig.bind_partial("too", "many", "args")
        ... except TypeError as exc:
        ...     raise PartialBindException.general(Foo.bar, exc)
        Traceback (most recent call last):
        PartialBindException: Failed to bind parameters to 'bar': ...
        """
        return cls(
            f"Failed to bind parameters to '{meth.method.__name__}': {e}"
        )

    @classmethod
    def missing_param(cls, param: str, meth: AnnouncementMethod) -> _BindExc:
        """Creates a `PartialBindException` for a missing parameter.

        Args:
            param (`str`): The name of the missing parameter.
            meth (`Callable[P, R]`): The method for which the parameter
                is missing.

        Returns:
            PartialBindException: The exception instance with the
                generated error message.

        Examples:
        >>> # Define a class with a method to decorate
        >>> class Foo:
        ...     def bar(self, instrument):
        ...         pass
        ...
        >>> from inspect import signature
        >>> sig = signature(Foo.bar)
        >>> bound_params = sig.bind_partial()  # Missing required parameters
        >>>
        >>> if "instrument" not in bound_params.args:
        ...    raise PartialBindException.missing_param("instrument", Foo())
        Traceback (most recent call last):
        PartialBindException: Failed to bind parameters to 'bar': ...
        """
        return cls(
            f"Parameter '{param}' missing for method "
            f"'{meth.method.__name__}'"
        )


# Type variables for InstrumentBoundAnnoMethod
_PBoundMeth = ParamSpec("_PBoundMeth")
_RBoundMeth = TypeVar("_RBoundMeth")
_WrappedBoundMeth: TypeAlias = Callable[_PBoundMeth, _RBoundMeth]


class BoundAnnouncementMethod(
    Generic[_PBoundMeth, _RBoundMeth], AnnouncementMethod
):
    """Represents a partially bound method with associated metadata.

    This class is used to wrap a method that has been partially bound
    with runtime arguments, including the `instrument` parameter. It
    facilitates logic, like validation, on the method with the runtime
    parameters before the method is executed.

    Args:
        method (`Callable[P, R]`): The decorated method to be
            managed.
        *args (`P.args`): Positional arguments to partially bind to the
            method.
        **kwargs (`P.kwargs`): Keyword arguments to partially bind to
            the method.

    Examples:
        >>> # Define a class with a decorated method
        >>> class Foo:
        ...     @announcements(BaseInstrument)
        ...     def bar(self, instrument):
        ...         pass
        ...
        >>> # Create an InstrumentBoundAnnoMethod instance
        >>> args = (Foo(), BaseInstrument())
        >>> bound_method = InstrumentBoundAnnoMethod(Foo.bar, *args)
        >>> bound_method
        InstrumentBoundAnnoMethod(method=<function Foo.bar at ...>,
                                  instrument=BaseInstrument())
    """

    def __init__(
        self,
        method: _WrappedBoundMeth,
        *args: _PBoundMeth.args,
        **kwargs: _PBoundMeth.kwargs,
    ) -> None:
        super().__init__(method)
        self.params = self.bind_partial(*args, **kwargs)

    @property
    def instrument(self) -> Any | None:
        """Returns the runtime `instrument` instance argument bound
        to the method.

        Returns:
            BaseInstrument: The bound `instrument` instance.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         pass
            ...
            >>> # Create an InstrumentBoundAnnoMethod instance
            >>> args = (Foo(), BaseInstrument())
            >>> bound_method = InstrumentBoundAnnoMethod(Foo.bar, *args)
            >>>
            >>> bound_method.instrument
            BaseInstrument()
        """
        return self.params.arguments.get("instrument")

    def bind_partial(
        self, *args: _PBoundMeth.args, **kwargs: _PBoundMeth.kwargs
    ) -> inspect.BoundArguments:
        # noinspection PyShadowingNames
        """Partially binds the provided arguments to the method's
        signature.

        Ensures that the required `instrument` parameter is present in
        the bound arguments.

        Args:
            *args (`P.args`): Positional arguments to bind.
            **kwargs (`P.kwargs`): Keyword arguments to bind.

        Returns:
            inspect.BoundArguments: The partially bound arguments.

        Raises:
            PartialBindException: If the binding fails or if the
                required `instrument` parameter is missing.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         pass
            ...
            >>> # Create an InstrumentBoundAnnoMethod instance
            >>> args = (Foo(), BaseInstrument())
            >>> bound_method = InstrumentBoundAnnoMethod(Foo.bar, *args)
            >>>
            >>> # bind_partial() is implicitly run on instantiation already
            >>> bound_method.bind_partial(*args)
            <BoundArguments (self=<Foo>, instrument=BaseInstrument)>
        """
        try:
            # Binds provided arguments to the method's signature.
            return self.signature.bind_partial(*args, **kwargs)
        except TypeError as e:
            raise PartialBindException.general(self, e)

    def execute(self) -> _RBoundMeth:
        """Executes the bound method.

        Returns:
            R: The return value of the executed method.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         print(f\"Executing with {instrument!r}\")
            ...
            >>> # Create an InstrumentBoundAnnoMethod instance
            >>> args = (Foo(), BaseInstrument())
            >>> bound_method = InstrumentBoundAnnoMethod(Foo.bar, *args)
            >>>
            >>> bound_method.execute()
            Executing with BaseInstrument()
        """
        response = self.method(*self.params.args, **self.params.kwargs)
        return response

    def __repr__(self) -> str:
        """Returns a string representation of the
        `InstrumentBoundAnnoMethod` instance.

        Returns:
            str: The string representation.

        Examples:
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument):
            ...         print(f\"Executing with {instrument!r}\")
            ...
            >>> # Create an InstrumentBoundAnnoMethod instance
            >>> args = (Foo(), BaseInstrument())
            >>> bound_method = InstrumentBoundAnnoMethod(Foo.bar, *args)
            >>> repr(bound_method)
            "InstrumentBoundAnnoMethod(method=<function Foo.bar at ...>,
                                       instrument=BaseInstrument())"
        """
        return (
            f"{self.__class__.__name__}(method={self.method!r}, "
            f"instrument={self.instrument!r})"
        )
