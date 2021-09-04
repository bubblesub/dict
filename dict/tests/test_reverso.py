"""Test the ReversoEngine class."""
from pathlib import Path
from unittest.mock import Mock, patch

from dict.__main__ import main


def test_reverso(data_dir: Path, capsys) -> None:
    """Test the reverso.net engine."""
    with patch(
        "requests.get",
        return_value=Mock(
            raise_for_status=Mock(),
            text=(data_dir / "reverso_in.html").read_text(),
        ),
    ) as fake_get:
        main(["-e", "reverso", "-N", "ridiculous", "-s", "pl", "-d", "en"])

    fake_get.assert_called_once()

    assert fake_get.mock_calls[0].args[0] == (
        "http://context.reverso.net/translation/"
        "polish-english/ridiculous?d=1"
    )

    assert (
        capsys.readouterr().out == (data_dir / "reverso_out.txt").read_text()
    )
