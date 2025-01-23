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
    `@announcement`. It also facilitates partially binding runtime
    arguments to the method before method execution.

    Args:
        meth (`Callable[P, R]`): The decorated method to be
            managed.

    Examples:
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> # Define a class with a decorated method
        >>> from domprob import announcement
        >>>
        >>> class Foo:
        ...     @announcement(SomeInstrument)
        ...     def bar(self, instrument: SomeInstrument) -> None:
        ...         pass
        ...
        >>> # Create an AnnouncementMethod instance
        >>> bar_method = AnnouncementMethod(Foo.bar)
        >>>
        >>> bar_method
        AnnouncementMethod(method=<function Foo.bar at ...>)
    """

    def __init__(self, meth: _WrappedMeth) -> None:
        self._meth = meth
        self._instruments = Instruments.from_method(self._meth)

    @property
    def method(self) -> _WrappedMeth:
        """The decorated method being managed.

        Returns:
            `Callable[P, R]`: The method.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import announcement
            >>>
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an AnnouncementMethod instance
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
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import announcement
            >>>
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an AnnouncementMethod instance
            >>> bar_method = AnnouncementMethod(Foo.bar)
            >>>
            >>> bar_method.instruments
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at...))
            >>> [i.__name__ for i in bar_method.instruments]
            ['SomeInstrument', 'SomeInstrument']
        """
        return self._instruments

    @property
    def signature(self) -> inspect.Signature:
        """The signature of the decorated method.

        Returns:
            inspect.Signature: The signature of the method.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import announcement
            >>>
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an AnnoMethod instance
            >>> bar_method = AnnouncementMethod(Foo.bar)
            >>>
            >>> bar_method.signature
            <Signature (self, instrument: ...SomeInstrument) -> None>
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
            BoundAnnouncementMethod: A new wrapper representing a
                partially bound method.

        Examples:
            >>> from domprob import announcement
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an AnnoMethod instance
            >>> bar_method = AnnouncementMethod(Foo.bar)
            >>>
            >>> # Binds method with instrument instance
            >>> instrument_instance = SomeInstrument()
            >>> bound_method = bar_method.bind(instrument_instance)
            >>> bound_method
            BoundAnnouncementMethod(method=<function Foo.bar at ...>, instrument=SomeInstrument)
        """
        return BoundAnnouncementMethod(self.method, *args, **kwargs)

    def __repr__(self) -> str:
        """Returns a string representation of the `AnnoMethod`
        instance.

        Returns:
            str: The string representation of the instance.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import announcement
            >>>
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an AnnouncementMethod instance
            >>> bar_method = AnnouncementMethod(Foo.bar)
            >>>
            >>> repr(bar_method)
            'AnnouncementMethod(method=<function Foo.bar at ...>)'
        """
        return f"{self.__class__.__name__}(method={self.method!r})"


class PartialBindException(AnnouncementException):
    """Exception raised when binding arguments to a method's signature
    fails.

    This exception is used to handle errors that occur during partial
    argument binding, including missing required parameters.
    """

    def __init__(self, method: AnnouncementMethod, exc: Exception) -> None:
        self.method = method
        self.exc = exc
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        m_name = ".".join(self.method.method.__qualname__.split(".")[-2:])
        m_name = f"{m_name}(...)"
        return f"Failed to bind parameters to {m_name}: {self.exc}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(method={self.method!r}, "
            f"exc={self.exc!r})"
        )


# Type variables for InstrumentBoundAnnoMethod
_PBoundMeth = ParamSpec("_PBoundMeth")
_RBoundMeth = TypeVar("_RBoundMeth")
_WrappedBoundMeth: TypeAlias = Callable[_PBoundMeth, _RBoundMeth]


class BoundAnnouncementMethod(
    Generic[_PBoundMeth, _RBoundMeth], AnnouncementMethod
):
    # pylint: disable=line-too-long
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
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> # Define a class with a decorated method
        >>> from domprob import announcement
        >>>
        >>> class Foo:
        ...     @announcement(SomeInstrument)
        ...     def bar(self, instrument: SomeInstrument) -> None:
        ...         pass
        ...
        >>> # Create an BoundAnnouncementMethod instance
        >>> args = (Foo(), SomeInstrument())
        >>> bound_method = BoundAnnouncementMethod(Foo.bar, *args)
        >>>
        >>> bound_method
        BoundAnnouncementMethod(method=<function Foo.bar at ...>, instrument=<...SomeInstrument object at...>)
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
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import announcement
            >>>
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an BoundAnnouncementMethod instance
            >>> args = (Foo(), SomeInstrument())
            >>> bound_method = BoundAnnouncementMethod(Foo.bar, *args)
            >>>
            >>> bound_method.instrument
            <....SomeInstrument object at...>
        """
        return self.params.arguments.get("instrument")

    def bind_partial(
        self, *args: _PBoundMeth.args, **kwargs: _PBoundMeth.kwargs
    ) -> inspect.BoundArguments:
        # noinspection PyShadowingNames
        # pylint: disable=line-too-long
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
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import announcement
            >>>
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an BoundAnnouncementMethod instance
            >>> args = (Foo(), SomeInstrument())
            >>> bound_method = BoundAnnouncementMethod(Foo.bar, *args)
            >>>
            >>> bound_method.bind_partial(*args)
            <BoundArguments (self=<...Foo object at...>, instrument=<...SomeInstrument object at...>)>
        """
        try:
            # Binds provided arguments to the method's signature.
            return self.signature.bind_partial(*args, **kwargs)
        except TypeError as e:
            raise PartialBindException(self, e)

    def execute(self) -> _RBoundMeth:
        """Executes the bound method.

        Returns:
            R: The return value of the executed method.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import announcement
            >>>
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> str:
            ...         return "Executed"
            ...
            >>> # Create an BoundAnnouncementMethod instance
            >>> args = (Foo(), SomeInstrument())
            >>> bound_method = BoundAnnouncementMethod(Foo.bar, *args)
            >>>
            >>> bound_method.execute()
            'Executed'
        """
        response = self.method(*self.params.args, **self.params.kwargs)
        return response

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        """Returns a string representation of the
        `InstrumentBoundAnnoMethod` instance.

        Returns:
            str: The string representation.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import announcement
            >>>
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> str:
            ...         return "Executed"
            ...
            >>> # Create an BoundAnnouncementMethod instance
            >>> args = (Foo(), SomeInstrument())
            >>> bound_method = BoundAnnouncementMethod(Foo.bar, *args)
            >>>
            >>> repr(bound_method)
            'BoundAnnouncementMethod(method=<function Foo.bar at...>, instrument=<...SomeInstrument object at...>)'
        """
        return (
            f"{self.__class__.__name__}(method={self.method!r}, "
            f"instrument={self.instrument!r})"
        )
