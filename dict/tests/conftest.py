"""Common pytest fixtures."""
from pathlib import Path

import pytest


@pytest.fixture(name="data_dir")
def fixture_data_dir() -> Path:
    """Return path to the test data directory.

    :return: path to the data directory
    """
    return Path(__file__).parent / "testdata"
