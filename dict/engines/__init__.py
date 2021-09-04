"""Definitions of dictionary engines."""
from .base import BaseEngine
from .reverso import ReversoEngine
from .urban import UrbanEngine

__all__ = [
    "BaseEngine",
    "ReversoEngine",
    "UrbanEngine",
]
