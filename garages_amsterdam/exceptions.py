"""Exceptions for Garages Amsterdam."""


class GaragesAmsterdamError(Exception):
    """Generic Garages Amsterdam exception."""


class GaragesAmsterdamConnectionError(GaragesAmsterdamError):
    """Garages Amsterdam connection exception."""


class GaragesAmsterdamResultsError(GaragesAmsterdamError):
    """Garages Amsterdam results exception."""
