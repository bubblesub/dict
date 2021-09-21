"""Test the SynonimEngine class."""
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dict.__main__ import main


@pytest.mark.parametrize(
    "test_file_prefix,test_phrase,status_code,expected_url",
    [
        (
            "synonim_valid",
            "miłość",
            200,
            "https://synonim.net/synonim/mi%C5%82o%C5%9B%C4%87",
        ),
        (
            "synonim_headerless",
            "uzupełniać",
            200,
            "https://synonim.net/synonim/uzupe%C5%82nia%C4%87",
        ),
        (
            "synonim_invalid",
            "fraktur",
            404,
            "https://synonim.net/synonim/fraktur",
        ),
    ],
)
def test_synonim(
    # pylint: disable=too-many-arguments
    data_dir: Path,
    capsys,
    test_file_prefix: str,
    status_code: int,
    test_phrase: str,
    expected_url: str,
) -> None:
    """Test the synonim.net engine."""
    fake_get = Mock(
        return_value=Mock(
            raise_for_status=Mock(),
            status_code=status_code,
            text=(data_dir / f"{test_file_prefix}_in.html").read_text(),
        ),
    )
    with patch(
        "requests.Session",
        return_value=Mock(get=fake_get),
    ):
        main(["-e", "synonim", "-N", test_phrase])

        fake_get.assert_called_once_with(expected_url)

    assert (
        capsys.readouterr().out
        == (data_dir / f"{test_file_prefix}_out.txt").read_text()
    )
