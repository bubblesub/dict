"""Definitions of dictionary engines."""
from .base import BaseEngine
from .reverso import ReversoEngine
from .sjp import SJPEngine
from .urban import UrbanEngine

__all__ = [
    "BaseEngine",
    "ReversoEngine",
    "SJPEngine",
    "UrbanEngine",
]
