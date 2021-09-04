"""Test the SJPEngine class."""
from pathlib import Path
from unittest.mock import Mock, patch

from dict.__main__ import main


def test_sjp(data_dir: Path, capsys) -> None:
    """Test the Słownik Języka Polskiego engine."""
    with patch(
        "requests.get",
        return_value=Mock(
            raise_for_status=Mock(),
            text=(data_dir / "sjp_in.html").read_text(),
        ),
    ) as fake_get:
        main(["-e", "sjp", "-N", "test"])

    fake_get.assert_called_once_with("http://sjp.pl/test")

    assert capsys.readouterr().out == (data_dir / "sjp_out.txt").read_text()
