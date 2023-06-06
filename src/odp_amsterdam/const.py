"""Asynchronous Python client providing Open Data information of Amsterdam."""

FILTER_OUT: list[str] = [
    "FP",
    "Fiets",
    "Dummy",
]

FILTER_NAMES: list[str] = [
    "CE-",
    "ZD-",
    "ZO-",
    "ZU-",
    "FJ212P34 ",
    "VRN-FJ212",
    "GRV020HNK ",
    " P ",
    " P4",
    " P5",
    " P21",
    " P22",
    " P23",
    " P24",
]

FILTER_UNKNOWN: list[str] = [
    "ONBEKEND",
    "Onbekend",
]

CORRECTIONS: list[str] = [
    "P1 ",
    "P3 ",
]
