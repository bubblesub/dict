"""Definition of the JMDict."""
import argparse
import gzip
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import IO, Optional, cast

import lxml
import xdg
from tqdm import tqdm

from dict.colors import COLOR_HIGHLIGHT, COLOR_RESET
from dict.engines.base import BaseEngine
from dict.http import download

DOWNLOAD_URL = "http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz"
XML_CACHE_PATH = Path(xdg.XDG_CACHE_HOME) / "jmdict.xml"
INDEX_CACHE_PATH = Path(xdg.XDG_CACHE_HOME) / "jmdict.jsonl"


def uniq(seq):
    """Return unique elements in the input collection, preserving the order.

    :param seq: sequence to filter
    :return: sequence with duplicate items removed
    """
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]


@dataclass
class JMDictKanji:
    """Kanji part of an JMDict result."""

    kanji: str
    pri: list[str]


@dataclass
class JMDictReading:
    """Reading part of an JMDict result."""

    reading: str
    pri: list[str]


@dataclass
class JMDictSense:
    """Sense part of an JMDict result."""

    information: Optional[str]
    meanings: list[str]
    parts_of_speech: list[str]
    miscellaneous: list[str]
    fields: Optional[str]


@dataclass
class JMDictResult:
    """A result from the JMDict engine."""

    ent_seq: int
    kanji: list[JMDictKanji]
    readings: list[JMDictReading]
    senses: list[JMDictSense]

    @property
    def tags(self) -> Iterable[str]:
        """Collect all tags from the senses, kanji and readings.

        :return: tags
        """
        return uniq(
            sum([kanji.pri for kanji in self.kanji], cast(list[str], []))
            + sum([reading.pri for reading in self.readings], [])
            + sum([sense.parts_of_speech for sense in self.senses], [])
        )


def entry_to_line(entry: JMDictResult) -> str:
    """Convert a JMDict result to a JSONL index line.

    Uses a compact representation to safe space, thus reducing the amount of
    text that the heuristic regexes need to process.

    :param entry: entry to convert
    :return: single line representation of the entry
    """
    return json.dumps(
        [
            entry.ent_seq,
            [
                {"k": kanji.kanji, **({"p": kanji.pri} if kanji.pri else {})}
                for kanji in entry.kanji
            ],
            [
                {
                    "r": reading.reading,
                    **({"p": reading.pri} if reading.pri else {}),
                }
                for reading in entry.readings
            ],
            [
                {
                    "m": sense.meanings,
                    "p": sense.parts_of_speech,
                    **(
                        {"M": sense.miscellaneous}
                        if sense.miscellaneous
                        else {}
                    ),
                    **({"f": sense.fields} if sense.fields else {}),
                    **({"i": sense.information} if sense.information else {}),
                }
                for sense in entry.senses
            ],
        ],
        ensure_ascii=False,
        check_circular=False,
        separators=(",", ":"),
    )


def entry_from_line(line: str) -> JMDictResult:
    """Convert a JSONL index line to a JMDict result.

    :param entry: single line representation of entry
    :return: converted entry
    """
    item = json.loads(line)
    ent_seq, kanji, readings, senses = item
    return JMDictResult(
        ent_seq=ent_seq,
        kanji=[
            JMDictKanji(kanji=kanji["k"], pri=kanji.get("p", []))
            for kanji in kanji
        ],
        readings=[
            JMDictReading(reading=reading["r"], pri=reading.get("p", []))
            for reading in readings
        ],
        senses=[
            JMDictSense(
                meanings=sense["m"],
                parts_of_speech=sense["p"],
                miscellaneous=sense.get("M", []),
                fields=sense.get("f", []),
                information=sense.get("i"),
            )
            for sense in senses
        ],
    )


def download_jmdict_xml_if_needed() -> None:
    """Download the JMDict XML file, if it does not exist yet."""
    if XML_CACHE_PATH.exists():
        return

    XML_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BytesIO() as handle:
        download(
            DOWNLOAD_URL,
            description="downloading the dictionary",
            handle=handle,
        )
        XML_CACHE_PATH.write_text(
            gzip.decompress(handle.getvalue()).decode("utf-8")
        )


def build_entries_from_xml(path: Path) -> Iterable[JMDictResult]:
    """Convert the JMDict XML file to JMDictResult entries.

    :param path: path to the JMDict XML dictionary file
    :return: a generator of results
    """
    root = lxml.etree.parse(str(path))
    entries = root.xpath("/JMdict/entry")
    with tqdm(entries, desc="building the index") as progress_bar:
        for entry in progress_bar:
            yield JMDictResult(
                ent_seq=int(entry.xpath("ent_seq/text()")[0]),
                kanji=[
                    JMDictKanji(
                        kanji=k_ele.xpath("keb/text()")[0],
                        pri=k_ele.xpath("ke_pri/text()"),
                    )
                    for k_ele in entry.xpath("k_ele")
                ],
                readings=[
                    JMDictReading(
                        reading=r_ele.xpath("reb/text()")[0],
                        pri=r_ele.xpath("re_pri/text()"),
                    )
                    for r_ele in entry.xpath("r_ele")
                ],
                senses=[
                    JMDictSense(
                        meanings=sense.xpath("gloss/text()"),
                        fields=sense.xpath("field/text()"),
                        parts_of_speech=sense.xpath("pos/text()"),
                        miscellaneous=sense.xpath("misc/text()"),
                        information=next(
                            iter(sense.xpath("information/text()")), None
                        ),
                    )
                    for sense in entry.xpath("sense")
                ],
            )


def create_jmdict_index_if_needed() -> None:
    """Create the JSONL index file, if it does not exist yet."""
    if INDEX_CACHE_PATH.exists():
        return

    with INDEX_CACHE_PATH.open("w") as handle:
        for entry in build_entries_from_xml(XML_CACHE_PATH):
            print(entry_to_line(entry), file=handle)


class JMDictEngine(BaseEngine[JMDictResult]):
    """JMDict engine (a Japanese textfile dictionary).

    Downloads JMDict UTF-8 gzipped file and transforms it into an index file,
    which is a JSONL file (one physical line = one self-contained JSON record).
    A query is considered a match when an input phrase is found in any
    significant property belonging to a logical record, but to boost the
    performance, it heuristically checks only records whose physical lines
    contain the input phrase.
    """

    names = ["jmdict"]

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[JMDictResult]:
        download_jmdict_xml_if_needed()
        create_jmdict_index_if_needed()

        pattern = re.compile(phrase, flags=re.I)

        with INDEX_CACHE_PATH.open("r") as handle:
            for line in handle:
                if pattern.search(line):
                    result = entry_from_line(line)
                    if (
                        any(
                            pattern.search(kanji.kanji)
                            for kanji in result.kanji
                        )
                        or any(
                            pattern.search(reading.reading)
                            for reading in result.readings
                        )
                        or any(
                            pattern.search(meaning)
                            for sense in result.senses
                            for meaning in sense.meanings
                        )
                    ):
                        yield result

    def print_results(
        self, results: Iterable[JMDictResult], file: IO[str]
    ) -> None:
        for result in results:
            for kanji in result.kanji:
                print(COLOR_HIGHLIGHT, end="", file=file)
                print(kanji.kanji, end="", file=file)
                print(COLOR_RESET, file=file)
            for reading in result.readings:
                print(COLOR_HIGHLIGHT, end="", file=file)
                print(reading.reading, end="", file=file)
                print(COLOR_RESET, file=file)
            print("[", end="", file=file)
            print(", ".join(result.tags), end="", file=file)
            print("]", file=file)
            for sense in result.senses:
                if sense.information:
                    print(sense.information)
                for meaning in sense.meanings:
                    print(meaning, file=file)
            print(file=file)
