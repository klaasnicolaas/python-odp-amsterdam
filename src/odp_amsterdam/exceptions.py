"""Asynchronous Python client providing Open Data information of Amsterdam."""


class ODPAmsterdamError(Exception):
    """Generic Open Data Platform exception."""


class ODPAmsterdamConnectionError(ODPAmsterdamError):
    """Open Data Platform connection exception."""


class ODPAmsterdamResultsError(ODPAmsterdamError):
    """Open Data Platform Amsterdam results exception."""
