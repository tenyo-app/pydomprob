from __future__ import annotations
import inspect
from collections.abc import Callable, ValuesView
from functools import cached_property
from inspect import BoundArguments, Parameter
from typing import (
    Any,
    Generic,
    ParamSpec,
    TypeVar,
    Concatenate,
    TypeAlias,
    Generator,
)

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.instruments import Instruments
from domprob.announcements.validation.orchestrator import (
    AnnouncementValidationOrchestrator,
)


class PartialBindException(AnnouncementException):
    # pylint: disable=line-too-long
    """Exception raised when binding arguments to a method's signature
    fails.

    This exception is used to handle errors that occur during partial
    argument binding, including missing required parameters.

    Attributes:
        meth (AnnouncementMethod): The method whose arguments failed
            to bind.
        e (Exception): The original exception that caused the
            failure.
    """

    def __init__(self, meth: AnnouncementMethod, e: Exception) -> None:
        self.meth = meth
        self.e = e
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Constructs the error message for the exception.

        The message includes the name of the method and the details of
        the original exception.

        Returns:
            str: A descriptive error message for the exception.
        """
        return f"Failed to bind parameters to {self.meth.meth!r}: {self.e}"

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        """Returns a string representation of the PartialBindException
        instance.

        The string includes the method and the original exception.

        Returns:
            str: A string representation of the exception instance.
        """
        return f"{self.__class__.__name__}(meth={self.meth!r}, e={self.e!r})"


_AnnounceMeth: TypeAlias = "AnnouncementMethod[_PMeth, _RMeth]"


class AnnouncementMethodBinder:
    """Handles argument binding for an `AnnouncementMethod`.

    This class provides utilities for binding arguments to the method
    signature of an `AnnouncementMethod`, both partially and fully. It
    ensures that the provided arguments match the method signature and
    raises an exception if binding fails.

    Attributes:
        announce_meth (AnnouncementMethod): The method wrapper
            instance for which arguments will be bound.

    Args:
        announce_meth (AnnouncementMethod): The method wrapper
            instance for which arguments will be bound.

    Examples:
        >>> from collections import OrderedDict
        >>> from domprob.announcements.method import (
        ...     AnnouncementMethod, AnnouncementMethodBinder
        ... )
        >>>
        >>> class Foo:
        ...     def bar(self, x: int = 5) -> None:
        ...         pass
        >>>
        >>> meth = AnnouncementMethod(Foo.bar)
        >>> binder = AnnouncementMethodBinder(meth)
        >>> binder
        AnnouncementMethodBinder(announce_meth=AnnouncementMethod(meth=<function Foo.bar at 0x...>))
    """

    _instr: str = "instrument"

    def __init__(self, announce_meth: _AnnounceMeth) -> None:
        self.announce_meth = announce_meth

    @staticmethod
    def _apply_defaults(b_params: BoundArguments) -> BoundArguments:
        """Applies default values to bound parameters.

        This method ensures that any parameters with default values
        that were not explicitly provided during binding are assigned
        their default values.

        Args:
            b_params (BoundArguments): The bound arguments for the
                method.

        Returns:
            BoundArguments: The updated bound arguments with defaults
                applied.

        Examples:
            >>> from collections import OrderedDict
            >>> from domprob.announcements.method import (
            ...     AnnouncementMethod, AnnouncementMethodBinder
            ... )
            >>>
            >>> class Foo:
            ...     def bar(self, x: int = 5) -> None:
            ...         pass
            >>>
            >>> meth = AnnouncementMethod(Foo.bar)
            >>> binder = AnnouncementMethodBinder(meth)
            >>>
            >>> signature = inspect.signature(Foo.bar)
            >>> b_arguments = BoundArguments(signature, OrderedDict())
            >>> b_arguments
            <BoundArguments ()>
            >>> binder._apply_defaults(b_arguments)
            <BoundArguments (x=5)>
        """
        b_params.apply_defaults()
        return b_params

    def _bind_partial(self, *args: Any, **kwargs: Any) -> BoundArguments:
        """Partially binds arguments to the method signature.

        This method allows binding a subset of the arguments required
        by the method. It does not enforce that all required parameters
        are provided.

        Args:
            *args (Any): Positional arguments to bind.
            **kwargs (Any): Keyword arguments to bind.

        Returns:
            BoundArguments: The partially bound arguments.

        Raises:
            PartialBindException: If the arguments cannot be bound to
                the method.

        Examples:
            >>> from collections import OrderedDict
            >>> from domprob.announcements.method import (
            ...     AnnouncementMethod, AnnouncementMethodBinder
            ... )
            >>>
            >>> class Foo:
            ...     def bar(self, x: int, bool_: bool = True) -> None:
            ...         pass
            >>>
            >>> meth = AnnouncementMethod(Foo.bar)
            >>> binder = AnnouncementMethodBinder(meth)
            >>>
            >>> b_arguments = binder._bind_partial(5, bool_=False)
            >>> b_arguments
            <BoundArguments (self=5, bool_=False)>

            >>> try:
            ...     _ = binder._bind_partial(5, y=10, bool_=False)
            ... except PartialBindException:
            ...     print("Failed partial binding")
            ...
            Failed partial binding
        """
        sig = self.get_signature()
        try:
            return sig.bind_partial(*args, **kwargs)
        except TypeError as e:
            raise PartialBindException(self.announce_meth, e) from e

    def bind(
        self, *args: Any, **kwargs: Any
    ) -> BoundAnnouncementMethod[_PMeth, _RMeth]:
        # pylint: disable=line-too-long
        """Fully binds arguments to the method signature and returns a
        bound method.

        This method ensures that all required arguments for the method
        are bound. It applies default values where applicable and
        returns a `BoundAnnouncementMethod` instance representing the
        method with its bound parameters.

        Args:
            *args (Any): Positional arguments to bind.
            **kwargs (Any): Keyword arguments to bind.

        Returns:
            BoundAnnouncementMethod: A wrapper around the method with
                bound arguments.

        Raises:
            PartialBindException: If binding fails due to missing or
                incorrect arguments.

        Examples:
            >>> from collections import OrderedDict
            >>> from domprob.announcements.method import (
            ...     AnnouncementMethod, AnnouncementMethodBinder
            ... )
            >>>
            >>> class Foo:
            ...     def bar(self, x: int, bool_: bool = True) -> None:
            ...         pass
            >>>
            >>> meth = AnnouncementMethod(Foo.bar)
            >>> binder = AnnouncementMethodBinder(meth)
            >>>
            >>> bound_meth = binder.bind(5)
            >>> bound_meth
            BoundAnnouncementMethod(announce_meth=AnnouncementMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=5, bool_=True)>)

            >>> try:
            ...     _ = binder._bind_partial(5, y=10)
            ... except PartialBindException:
            ...     print("Failed partial binding")
            ...
            Failed partial binding
        """
        b_params = self._bind_partial(*args, **kwargs)
        b_params = self._apply_defaults(b_params)
        return BoundAnnouncementMethod(self.announce_meth, b_params)

    def _rn(self, param: inspect.Parameter) -> inspect.Parameter:
        return param.replace(name=self._instr)

    def _infer_ann_params(
        self, params: ValuesView[inspect.Parameter]
    ) -> Generator[Parameter, Any, None] | None:
        instrums = (i for i, _ in self.announce_meth.supp_instrums)
        for param in params:
            ann = param.annotation
            if ann is inspect.Parameter.empty:  # No annotation defined
                continue
            if all(i for i in instrums if i == ann or issubclass(i, ann)):
                return (self._rn(p) if p is param else p for p in params)
        return None

    def _infer_pos_params(
        self, params: ValuesView[inspect.Parameter]
    ) -> Generator[inspect.Parameter, None, None]:
        params_iter = iter(params)
        try:
            first_param = next(params_iter)
        except StopIteration:
            return
        # Hacky 'self' check - could fail if first arg in instance method
        # doesn't follow convention
        if first_param.name != "self":
            first_param = self._rn(first_param)
        yield first_param
        try:
            second_param = next(params_iter)
        except StopIteration:
            return
        if first_param.name != "instrument":
            second_param = self._rn(second_param)
        yield second_param
        yield from params_iter

    def get_signature(self) -> inspect.Signature:
        """Retrieves the method signature of the wrapped
        `AnnouncementMethod`.

        If an 'instrument' argument is not defined, manipulation
        occurs before binding to enable instrument access on the
        `BoundAnnouncementMethod` wrapper class. The parameters in the
        method signature will change so that a parameter is renamed to
        'instrument'. In priority order, an attempt is made to
        manipulate the parameters in the following ways:

        1. The parameters type hint annotations will be inspected. It
           will check if the type hint of an argument defined in the
           method signature is the same typemor a parent type of that
           defined in all announcement decorators that wrap the
           associated method.

           .. Warning:: If multiple parameters exist that match the
              type hinting criteria above, the leftmost parameter will
              take precedence.

        2. Fallback. If neither an 'instrument' parameter is defined or
           a parameter with the correct type hint annotations are
           defined, we will assign the first parameter (exc. 'self') as
           the 'instrument' parameter.

        Returns:
            inspect.Signature: The signature of the decorated method.

        Examples:
            >>> def example_method(x: int, y: str) -> None:
            ...     pass
            ...
            >>> method = AnnouncementMethod(example_method)
            >>> binder = AnnouncementMethodBinder(method)
            >>> binder.get_signature()
            <Signature (instrument: 'int', y: 'str') -> 'None'>
        """
        sig = inspect.signature(self.announce_meth.meth)
        if self._instr in sig.parameters.keys():
            return sig
        inf_params = self._infer_ann_params(sig.parameters.values())
        if inf_params is None:  # Fallback - infer instrument to be first arg
            inf_params = self._infer_pos_params(sig.parameters.values())
        return sig.replace(parameters=tuple(inf_params))

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        """Returns a string representation of the
        `AnnouncementMethodBinder` instance.

        Returns:
            str: A string representation of the instance.

        Examples:
            >>> def example_method():
            ...     pass
            ...
            >>> method = AnnouncementMethod(example_method)
            >>> binder = AnnouncementMethodBinder(method)
            >>> repr(binder)
            'AnnouncementMethodBinder(announce_meth=AnnouncementMethod(meth=<function example_method at 0x...>))'
        """
        return (
            f"{self.__class__.__name__}(announce_meth={self.announce_meth!r})"
        )


# Typing helpers: Describes the wrapped method signature for wrapper
_PMeth = ParamSpec("_PMeth")
_RMeth = TypeVar("_RMeth")


class BaseAnnouncementMethod(Generic[_PMeth, _RMeth]):
    """Base class for announcement-related methods.

    This class provides shared functionality for both
    `AnnouncementMethod` and `BoundAnnouncementMethod`, including
    caching and retrieval of supported instruments.

    Args:
        meth (Callable): The method associated with this announcement.
    """

    def __init__(
        self,
        meth: Callable[_PMeth, _RMeth],
        supp_instrums: Instruments | None = None,
    ) -> None:
        self._meth = meth
        self._supp_instrums = supp_instrums

    @property
    def meth(self) -> Callable[_PMeth, _RMeth]:
        """Returns the decorated method.

        This method represents the underlying method associated with
        the announcement.

        Returns:
            Callable[_PMeth, _RMeth]: The method associated with this
                announcement.

        Examples:
            >>> from domprob.announcements.method import BaseAnnouncementMethod
            >>>
            >>> def example_method():
            ...     pass
            ...
            >>> base = BaseAnnouncementMethod(example_method)
            >>> base.meth
            <function example_method at 0x...>
        """
        return self._meth

    @cached_property
    def supp_instrums(self) -> Instruments:
        """Returns the supported instruments for this method.

        This property retrieves the metadata associated with the
        decorated method, indicating which instruments are supported.

        Returns:
            Instruments: An `Instruments` object containing metadata
                about the method’s supported instruments.

        Examples:
            >>> from domprob.announcements.method import BaseAnnouncementMethod
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> def example_method(instrument: SomeInstrument) -> None:
            ...     pass
            ...
            >>> base = BaseAnnouncementMethod(example_method)
            >>> base.supp_instrums
            Instruments(metadata=AnnouncementMetadata(method=<function example_method at 0x...>))
        """
        return self._supp_instrums or Instruments.from_method(self.meth)

    def __repr__(self) -> str:
        """Returns a string representation of the `BaseAnnouncement`
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
            >>> bar_method = BaseAnnouncementMethod(Foo.bar)
            >>>
            >>> repr(bar_method)
            'BaseAnnouncementMethod(meth=<function Foo.bar at 0x...>)'
        """
        return f"{self.__class__.__name__}(meth={self.meth!r})"


class AnnouncementMethod(BaseAnnouncementMethod, Generic[_PMeth, _RMeth]):
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
        AnnouncementMethod(meth=<function Foo.bar at 0x...>)
    """

    def __init__(
        self,
        meth: Callable[_PMeth, _RMeth],
        supp_instrums: Instruments[Any] | None = None,
    ) -> None:
        super().__init__(meth, supp_instrums)
        self._binder = AnnouncementMethodBinder(self)

    @classmethod
    def from_callable(
        cls, meth: Callable[_PMeth, _RMeth]
    ) -> _AnnounceMeth | None:
        """Creates an `AnnouncementMethod` instance from a callable if
        it supports instruments.

        This class method checks if the provided callable (`meth`) has
        associated metadata for supported instruments. If it does, an
        `AnnouncementMethod` instance is created and returned.
        Otherwise, `None` is returned.

        Args:
            meth (Callable[_PMeth, _RMeth]): The method or function to
                be wrapped as an `AnnouncementMethod`.

        Returns:
            AnnouncementMethod[_PMeth, _RMeth] | None:
                - An instance of `AnnouncementMethod` if the callable
                  has associated metadata.
                - `None` if the callable does not support instruments.

        Example:
            >>> from domprob import announcement
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         print(f"Instrument: {instrument}")
            ...
            >>> # Create an AnnouncementMethod instance from a method
            >>> announce_meth = AnnouncementMethod.from_callable(Foo.bar)
            >>> assert isinstance(announce_meth, AnnouncementMethod)
            >>> print(announce_meth)
            AnnouncementMethod(meth=<function Foo.bar at 0x...>)

            >>> # Attempt to create an AnnouncementMethod from a method without metadata
            >>> def no_announcement_method():
            ...     pass
            ...
            >>> assert AnnouncementMethod.from_callable(no_announcement_method) is None
        """
        supp_instrums = Instruments.from_method(meth)
        return cls(meth, supp_instrums) if supp_instrums else None

    def bind(
        self, cls_instance: Any, *args: _PMeth.args, **kwargs: _PMeth.kwargs
    ) -> BoundAnnouncementMethod[Concatenate[Any, _PMeth], _RMeth]:
        # noinspection PyShadowingNames
        # pylint: disable=line-too-long
        """Binds passed parameters to the method, returning a
        partially bound version.

        This method partially binds the provided runtime arguments. It
        returns a `BoundAnnouncementMethod` object that represents the
        partially bound method, which can later be executed with
        additional arguments if needed.

        Args:
            cls_instance (`Any`): The class instance to bind. This is
                the `self` arg defined in instance methods.
            *args (P.args): Additional positional arguments to bind to
                the method.
            **kwargs (P.kwargs): Additional keyword arguments to bind
                to the method.

        Returns:
            BoundAnnouncementMethod: A new wrapper representing a
                partially bound method.

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
            >>> # Create an instance of the class and instrument
            >>> instrument_instance = SomeInstrument()
            >>> foo = Foo()
            >>>
            >>> # Binds method with instrument instance
            >>> args = (foo, instrument_instance)
            >>> bound_method = bar_method.bind(*args)
            >>> bound_method
            BoundAnnouncementMethod(announce_meth=AnnouncementMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=<domprob.announcements.method.Foo object at 0x...>, instrument=<domprob.announcements.method.SomeInstrument object at 0x...>)>)
        """
        return self._binder.bind(cls_instance, *args, **kwargs)


class BoundAnnouncementMethod(BaseAnnouncementMethod, Generic[_PMeth, _RMeth]):
    # pylint: disable=line-too-long
    """Represents a partially bound method with associated metadata.

    This class is used to wrap a method that has been partially bound
    with runtime arguments, including the `instrument` parameter. It
    facilitates logic, like validation, on the method with the runtime
    parameters before the method is executed.

    Args:
        announce_meth (AnnouncementMethod): Original method wrapper
            that's had parameters bound.
        bound_params (inspect.BoundArguments): Parameters that are
            bound to a method.

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
        >>> from collections import OrderedDict
        >>> announce_meth = AnnouncementMethod(Foo.bar)
        >>> sig = inspect.signature(Foo.bar)
        >>> b_args = BoundArguments(sig, OrderedDict())
        >>> # Bind the arguments correctly
        >>> bound = sig.bind_partial(Foo(), SomeInstrument())
        >>> b_args.arguments = bound.arguments
        >>> bound_method = BoundAnnouncementMethod(announce_meth, b_args)
        >>>
        >>> bound_method
        BoundAnnouncementMethod(announce_meth=AnnouncementMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=<domprob.announcements.method.Foo object at 0x...>, instrument=<domprob.announcements.method.SomeInstrument object at 0x...>)>)
    """

    def __init__(
        self,
        announce_meth: AnnouncementMethod[_PMeth, _RMeth],
        bound_params: inspect.BoundArguments,
    ) -> None:
        super().__init__(announce_meth.meth)
        self._announce_meth = announce_meth
        self._params = bound_params
        self._validator = AnnouncementValidationOrchestrator()

    @property
    def params(self) -> inspect.BoundArguments:
        """Returns the bound arguments applied to the method.

        Returns:
            `inspect.BoundArguments`: Bound arguments applied to the
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
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an BoundAnnouncementMethod instance
            >>> import inspect
            >>> from collections import OrderedDict
            >>> from domprob.announcements.method import (
            ...     AnnouncementMethod, BoundAnnouncementMethod
            ... )
            >>>
            >>> announce_meth = AnnouncementMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundAnnouncementMethod(announce_meth, b_args)
            >>>
            >>> bound_method.instrument
            <....SomeInstrument object at 0x...>
        """
        return self._params

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
            >>> import inspect
            >>> from collections import OrderedDict
            >>> from domprob.announcements.method import (
            ...     AnnouncementMethod, BoundAnnouncementMethod
            ... )
            >>>
            >>> announce_meth = AnnouncementMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundAnnouncementMethod(announce_meth, b_args)
            >>>
            >>> bound_method.instrument
            <....SomeInstrument object at 0x...>
        """
        return self.params.arguments.get("instrument")

    def execute(self) -> _RMeth:
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
            >>> from collections import OrderedDict
            >>> announce_meth = AnnouncementMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundAnnouncementMethod(announce_meth, b_args)
            >>>
            >>> bound_method.execute()
            'Executed'
        """
        return self.meth(*self.params.args, **self.params.kwargs)

    def validate(self) -> None:
        """Validates the bound method using the validation
        orchestrator.

        This method ensures that all runtime arguments and metadata
        associated with the bound method meet the specified validation
        criteria. If validation fails, an appropriate exception is
        raised.

        Raises:
            AnnouncementValidationException: If any validation rule
                fails.

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
            >>> from collections import OrderedDict
            >>> announce_meth = AnnouncementMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundAnnouncementMethod(announce_meth, b_args)
            >>>
            >>> # Validate the bound method
            >>> bound_method.validate()
        """
        self._validator.validate(self)

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
            >>> from collections import OrderedDict
            >>> announce_meth = AnnouncementMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundAnnouncementMethod(announce_meth, b_args)
            >>>
            >>> repr(bound_method)
            'BoundAnnouncementMethod(announce_meth=AnnouncementMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=<domprob.announcements.method.Foo object at 0x...>, instrument=<domprob.announcements.method.SomeInstrument object at 0x...>)>)'

        """
        params = (
            f"announce_meth={self._announce_meth!r}, "
            f"bound_params={self.params!r}"
        )
        return f"{self.__class__.__name__}({params})"
