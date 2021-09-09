"""Definition of the WordHippoEngine."""
import argparse
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import IntEnum
from typing import IO, Optional
from urllib.parse import quote

import lxml.etree
import requests

from dict.colors import COLOR_HIGHLIGHT, COLOR_RESET
from dict.engines.base import BaseEngine
from dict.pager import print_in_columns

MEANINGS_URL = (
    "https://www.wordhippo.com/what-is/the-meaning-of-the-word/{}.html"
)
SYNONYMS_URL = "https://www.wordhippo.com/what-is/another-word-for/{}.html"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
)


class WordHippoLookupMode(IntEnum):
    """WordHippo engine lookup target."""

    SYNONYMS = 1
    MEANINGS = 2


def _get_text_from_node(node: lxml.etree.Element) -> str:
    return "".join(node.itertext())


@dataclass
class BaseWordHippoResult:
    """Base WordHippo engine result."""

    word_type: str

    @property
    def column_size(self) -> int:
        """Maximum item length to align the results in a table.

        :return: max item length
        """
        raise NotImplementedError("not implemented")  # pragma: no cover

    def print_to_stream(self, file: IO[str], column_size: int) -> None:
        """Print self to the given stream.

        :param file: output stream
        :param column_size: column size for aligning the results in a table
        """
        raise NotImplementedError("not implemented")  # pragma: no cover


TLookupFunc = Callable[[str], Iterable[BaseWordHippoResult]]


@dataclass
class WordHippoMeaningResult(BaseWordHippoResult):
    """WordHippo engine meaning result."""

    meanings: list[str]

    @property
    def column_size(self) -> int:
        return max(map(len, self.meanings))

    def print_to_stream(self, file: IO[str], column_size: int) -> None:
        print(COLOR_HIGHLIGHT + self.word_type + COLOR_RESET, file=file)
        for meaning in self.meanings:
            print(f"- {meaning}", file=file)
        print(file=file)


@dataclass
class WordHippoSynonymResult(BaseWordHippoResult):
    """WordHippo engine synonym result."""

    word_desc: str
    synonyms: list[str]

    @property
    def column_size(self) -> int:
        return max(map(len, self.synonyms))

    def print_to_stream(self, file: IO[str], column_size: int) -> None:
        print(
            COLOR_HIGHLIGHT
            + f"{self.word_type} ({self.word_desc})"
            + COLOR_RESET,
            file=file,
        )
        print_in_columns(
            (synonym for synonym in self.synonyms),
            column_size=column_size,
            file=file,
        )


class WordHippoEngine(BaseEngine[BaseWordHippoResult]):
    """WordHippo engine."""

    names = ["wordhippo"]

    @staticmethod
    def decorate_arg_parser(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-s",
            action="store_const",
            dest="lookup_mode",
            const=WordHippoLookupMode.SYNONYMS,
            help="look for synonyms (default)",
        )
        parser.add_argument(
            "-m",
            action="store_const",
            dest="lookup_mode",
            const=WordHippoLookupMode.MEANINGS,
            help="look for meanings",
        )

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[BaseWordHippoResult]:
        func_map: dict[Optional[int], TLookupFunc] = {
            WordHippoLookupMode.SYNONYMS: self.get_synonyms,
            WordHippoLookupMode.MEANINGS: self.get_meanings,
            None: self.get_synonyms,
        }
        func = func_map[args.lookup_mode]
        yield from func(phrase)

    @staticmethod
    def get_synonyms(phrase: str) -> Iterable[WordHippoSynonymResult]:
        """Get synonyms for the given phrase.

        :param phrase: phrase to look up
        :return: a generator of synonyms
        """
        url = SYNONYMS_URL.format(quote(phrase))
        response = requests.get(url, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        doc = lxml.etree.HTML(response.text)
        for word_desc_node in doc.cssselect("div.tabdesc"):
            word_type_node = word_desc_node.getprevious()
            related_word_nodes = word_desc_node.getnext().cssselect("div.wb a")
            yield WordHippoSynonymResult(
                word_type=(word_type_node.text or "").strip(),
                word_desc=_get_text_from_node(word_desc_node),
                synonyms=list(map(_get_text_from_node, related_word_nodes)),
            )

    @staticmethod
    def get_meanings(phrase: str) -> Iterable[WordHippoMeaningResult]:
        """Get meanings for the given phrase.

        :param phrase: phrase to look up
        :return: a generator of meanings
        """
        url = MEANINGS_URL.format(quote(phrase))
        response = requests.get(url, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        doc = lxml.etree.HTML(response.text)
        for word_type_node in doc.cssselect("div.defv2wordtype"):
            meaning_word_nodes = word_type_node.getnext().cssselect(
                ".topleveldefinition li"
            )
            yield WordHippoMeaningResult(
                word_type=_get_text_from_node(word_type_node),
                meanings=list(map(_get_text_from_node, meaning_word_nodes)),
            )

    def print_results(
        self, results: Iterable[BaseWordHippoResult], file: IO[str]
    ) -> None:
        column_size = max(result.column_size for result in results)
        for result in results:
            result.print_to_stream(file=file, column_size=column_size)
