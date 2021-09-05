"""Definitions of dictionary engines."""
from .base import BaseEngine
from .edict2 import Edict2Engine
from .jisho import JishoEngine
from .reverso import ReversoEngine
from .sjp import SJPEngine
from .urban import UrbanEngine
from .wordhippo import WordHippoEngine

__all__ = [
    "BaseEngine",
    "Edict2Engine",
    "JishoEngine",
    "ReversoEngine",
    "SJPEngine",
    "UrbanEngine",
]
