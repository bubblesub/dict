"""Test the SJPEngine class."""
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dict.__main__ import main


@pytest.mark.parametrize(
    "test_file_prefix,test_phrase,expected_url",
    [
        ("sjp_valid", "test", "http://sjp.pl/test"),
        ("sjp_invalid", "wymyśleć", "http://sjp.pl/wymy%C5%9Ble%C4%87"),
    ],
)
def test_sjp(
    data_dir: Path,
    capsys,
    test_file_prefix: str,
    test_phrase: str,
    expected_url: str,
) -> None:
    """Test the Słownik Języka Polskiego engine."""
    with patch(
        "requests.get",
        return_value=Mock(
            raise_for_status=Mock(),
            text=(data_dir / f"{test_file_prefix}_in.html").read_text(),
        ),
    ) as fake_get:
        main(["-e", "sjp", "-N", test_phrase])

    fake_get.assert_called_once_with(expected_url)

    assert (
        capsys.readouterr().out
        == (data_dir / f"{test_file_prefix}_out.txt").read_text()
    )
