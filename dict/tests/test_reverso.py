"""Test the ReversoEngine class."""
from pathlib import Path
from unittest.mock import patch

from dict.__main__ import main


def test_reverso(data_dir: Path, capsys) -> None:
    """Test the reverso.net engine."""
    with (data_dir / "reverso_in.txt").open("rb") as handle:
        with patch(
            "urllib.request.urlopen", return_value=handle
        ) as fake_urlopen:
            main(
                [
                    "-e",
                    "reverso",
                    "--no-pager",
                    "ridiculous",
                    "-s",
                    "pl",
                    "-d",
                    "en",
                ]
            )

    fake_urlopen.assert_called_once()

    assert fake_urlopen.mock_calls[0].args[0].full_url == (
        "http://context.reverso.net/translation/"
        "polish-english/ridiculous?d=1"
    )

    assert (
        capsys.readouterr().out == (data_dir / "reverso_out.txt").read_text()
    )
