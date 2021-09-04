"""Test the JishoEngine class."""
import json
from pathlib import Path
from unittest.mock import Mock, patch

from dict.__main__ import main


def test_jisho(data_dir: Path, capsys) -> None:
    """Test the jisho.org engine."""
    with patch(
        "requests.get",
        return_value=Mock(
            raise_for_status=Mock(),
            json=Mock(
                return_value=json.loads(
                    (data_dir / "jisho_in.json").read_text()
                )
            ),
        ),
    ) as fake_get:
        main(["-e", "jisho", "-N", "test"])

    fake_get.assert_called_once_with(
        "http://jisho.org/api/v1/search/words", {"keyword": "test"}
    )

    assert capsys.readouterr().out == (data_dir / "jisho_out.txt").read_text()
