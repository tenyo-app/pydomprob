from domprob.base_exc import DomprobException


class SensorException(DomprobException):
    """Base exception class for errors related to the `@sensor`
    functionality.

    This serves as a parent class for all exceptions raised within
    the sensors framework.
    """
