from collections.abc import Generator
from typing import ParamSpec, Protocol, TypeVar, runtime_checkable, Any

from domprob.announcements.method import AnnouncementMethod

# Typing helpers: defines an @announcement method signature
_P = ParamSpec("_P")
_R_co = TypeVar("_R_co", bound=Any, covariant=True)
_AnnounceSig = AnnouncementMethod[_P, _R_co]


# pylint: disable=too-few-public-methods
@runtime_checkable
class ObservationProtocol(Protocol[_P, _R_co]):
    """Protocol defining the structure of domain observations that
    provide announcements.

    Classes implementing this protocol must define a `@classmethod`
    named `announcements` that returns a `Generator` of
    `AnnouncementMethod` instances.

    This protocol is `@runtime_checkable`, meaning
    `isinstance(obj, ObservationProtocol)` can be used to verify
    implementation at runtime.

    Type Parameters:
        _P (ParamSpec): Represents the parameters accepted by the
            announcement method.
        _R_co (TypeVar): Represents the return type of the announcement
            method.

    Example:

        >>> class ConcreteObservation:
        ...     @classmethod
        ...     def announcements(cls) -> Generator[AnnouncementMethod, None, None]:
        ...         yield AnnouncementMethod(lambda x: x)
        ...
        >>> assert isinstance(ConcreteObservation, ObservationProtocol)
    """

    @classmethod
    def announcements(cls) -> Generator[_AnnounceSig, None, None]:
        """Retrieve all announcement methods defined in the class.

        Returns:
            Generator[_AnnounceSig, None, None]: A generator yielding
                `AnnouncementMethod` instances.
        """

    def __repr__(self): ...
