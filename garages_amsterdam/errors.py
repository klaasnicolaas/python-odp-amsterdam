"""Error handling for garages_amsterdam."""


class GaragesAmsterdamException(Exception):
    """Base error for Garages Amsterdam."""


class RequestError(GaragesAmsterdamException):
    """Unable to fulfill request."""


class ResponseError(GaragesAmsterdamException):
    """Invalid response."""


class UnknownError(GaragesAmsterdamException):
    """Invalid response."""


ERRORS = {
    1: RequestError,
    2: ResponseError,
    3: UnknownError,
}


def raise_error(err, errortype=None):
    """Raise the appropriate error."""
    cls = ERRORS.get(errortype, GaragesAmsterdamException)
    raise cls(err)