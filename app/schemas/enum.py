from enum import StrEnum, auto


class DetectorDecision(StrEnum):
    ALLOW = auto()
    BLOCK = auto()
