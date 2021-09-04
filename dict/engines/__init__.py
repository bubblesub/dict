"""Definitions of dictionary engines."""
from .base import BaseEngine
from .jisho import JishoEngine
from .reverso import ReversoEngine
from .sjp import SJPEngine
from .urban import UrbanEngine

__all__ = [
    "BaseEngine",
    "JishoEngine",
    "ReversoEngine",
    "SJPEngine",
    "UrbanEngine",
]
