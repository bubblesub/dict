"""Test the Edict2Engine class."""
import gzip
from pathlib import Path
from unittest.mock import Mock, patch

from dict.__main__ import main
from dict.engines.edict2 import (
    Edict2Glossary,
    Edict2Japanese,
    Edict2Result,
    parse_edict2_line,
)


def test_parse_edict2_line() -> None:
    """Test the parse_edict2_line function."""
    assert parse_edict2_line(
        "憂鬱(P);憂うつ;憂欝;悒鬱;幽鬱;幽欝;悒欝 [ゆううつ] /(n,adj-na) "
        "depression/melancholy/dejection/gloom/despondency/"
        "(P)/EntL1605640X/"
    ) == Edict2Result(
        ent_seq="1605640",
        has_audio=True,
        tags=["P", "adj-na", "n"],
        japanese=[
            Edict2Japanese(
                kanji="憂鬱", kana="ゆううつ", kanji_tags=["P"], kana_tags=[]
            ),
            Edict2Japanese(
                kanji="憂うつ", kana="ゆううつ", kanji_tags=[], kana_tags=[]
            ),
            Edict2Japanese(
                kanji="憂欝", kana="ゆううつ", kanji_tags=[], kana_tags=[]
            ),
            Edict2Japanese(
                kanji="悒鬱", kana="ゆううつ", kanji_tags=[], kana_tags=[]
            ),
            Edict2Japanese(
                kanji="幽鬱", kana="ゆううつ", kanji_tags=[], kana_tags=[]
            ),
            Edict2Japanese(
                kanji="幽欝", kana="ゆううつ", kanji_tags=[], kana_tags=[]
            ),
            Edict2Japanese(
                kanji="悒欝", kana="ゆううつ", kanji_tags=[], kana_tags=[]
            ),
        ],
        glossaries=[
            Edict2Glossary(
                english="depression", tags=[], field=None, related=[]
            ),
            Edict2Glossary(
                english="melancholy", tags=[], field=None, related=[]
            ),
            Edict2Glossary(
                english="dejection", tags=[], field=None, related=[]
            ),
            Edict2Glossary(english="gloom", tags=[], field=None, related=[]),
            Edict2Glossary(
                english="despondency", tags=[], field=None, related=[]
            ),
        ],
    )


def test_edict2(tmp_path: Path, data_dir: Path, capsys) -> None:
    """Test the edict2 engine."""
    test_content = gzip.compress(
        (data_dir / "edict2_in.txt").read_text().encode("euc-jp")
    )

    with patch(
        "dict.engines.edict2.CACHE_PATH", tmp_path / "edict2.txt"
    ), patch(
        "requests.get",
        return_value=Mock(
            raise_for_status=Mock(),
            headers={"Content-Length": len(test_content)},
            iter_content=Mock(return_value=[test_content]),
        ),
    ) as fake_get:
        main(["-e", "edict", "-N", "憂鬱"])

    fake_get.assert_called_once_with(
        "http://ftp.edrdg.org/pub/Nihongo/edict2.gz", stream=True
    )

    assert capsys.readouterr().out == (data_dir / "edict2_out.txt").read_text()
