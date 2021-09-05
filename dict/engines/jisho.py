"""Definition of the JishoEngine."""
import argparse
from collections.abc import Iterable
from dataclasses import dataclass
from typing import IO, Optional

import requests

from dict.colors import COLOR_HIGHLIGHT, COLOR_RESET
from dict.engines.base import BaseEngine


@dataclass
class JishoResultJapaneseInfo:
    """Information on Japanese spelling from a Jisho.org result."""

    word: Optional[str]
    reading: Optional[str]


@dataclass
class JishoResult:
    """A result from the jisho.org engine."""

    japanese: list[JishoResultJapaneseInfo]
    meanings: list[str]


class JishoEngine(BaseEngine[JishoResult]):
    """Jisho.org engine."""

    names = ["jisho"]

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[JishoResult]:
        url = "http://jisho.org/api/v1/search/words"
        response = requests.get(url, {"keyword": phrase})
        response.raise_for_status()
        content = response.json()

        for entry in content["data"]:
            yield JishoResult(
                japanese=[
                    JishoResultJapaneseInfo(
                        word=item.get("word"),
                        reading=item.get("reading"),
                    )
                    for item in entry["japanese"]
                ],
                meanings=[
                    definition
                    for sense in entry["senses"]
                    for definition in sense.get("english_definitions", [])
                ],
            )

    def print_results(
        self, results: Iterable[JishoResult], file: IO[str]
    ) -> None:
        for result in results:
            for jp_info in result.japanese:
                print(COLOR_HIGHLIGHT, end="", file=file)
                if jp_info.word and jp_info.reading:
                    print(
                        f"{jp_info.word} ({jp_info.reading})",
                        end="",
                        file=file,
                    )
                elif jp_info.word:
                    print(jp_info.word, end="", file=file)
                else:
                    print(jp_info.reading, end="", file=file)
                print(COLOR_RESET, file=file)

            for meaning in result.meanings:
                print(meaning, file=file)

            print(file=file)
