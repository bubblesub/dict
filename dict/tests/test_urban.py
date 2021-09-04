"""Test the UrbanEngine class."""
import json
from pathlib import Path
from unittest.mock import Mock, patch

from dict.__main__ import main


def test_urban(data_dir: Path, capsys) -> None:
    """Test the Urban Dictionary engine."""
    with patch(
        "requests.get",
        return_value=Mock(
            raise_for_status=Mock(),
            json=Mock(
                return_value=json.loads(
                    (data_dir / "urban_in.json").read_text()
                )
            ),
        ),
    ) as fake_get:
        main(["-e", "urban", "-N", "sizzle"])

    fake_get.assert_called_once_with(
        "http://api.urbandictionary.com/v0/define", {"term": "sizzle"}
    )

    assert capsys.readouterr().out == (data_dir / "urban_out.txt").read_text()
