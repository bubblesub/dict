"""Test the WordHippoEngine class."""
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dict.__main__ import main


@pytest.mark.parametrize(
    "test_file_prefix,args,expected_url",
    [
        (
            "wordhippo_synonyms",
            ["-s", "test"],
            (
                "https://www.wordhippo.com/what-is/"
                "another-word-for/test.html"
            ),
        ),
        (
            "wordhippo_meanings",
            ["-d", "test"],
            (
                "https://www.wordhippo.com/what-is/"
                "the-meaning-of-the-word/test.html"
            ),
        ),
    ],
)
def test_word_hippo(
    data_dir: Path,
    capsys,
    test_file_prefix: str,
    args: list[str],
    expected_url: str,
) -> None:
    """Test the WordHippo engine."""
    with patch(
        "requests.get",
        return_value=Mock(
            raise_for_status=Mock(),
            text=(data_dir / f"{test_file_prefix}_in.html").read_text(),
        ),
    ) as fake_get:
        main(["-e", "wordhippo", "-N", *args])

    fake_get.assert_called_once()
    assert fake_get.mock_calls[0].args[0] == expected_url

    assert (
        capsys.readouterr().out
        == (data_dir / f"{test_file_prefix}_out.txt").read_text()
    )
