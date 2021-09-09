"""Definition of SynonimEngine."""
import argparse
import urllib.parse
from collections.abc import Iterable
from dataclasses import dataclass
from typing import IO

import lxml.html
import requests

from dict.colors import COLOR_HIGHLIGHT, COLOR_RESET
from dict.engines.base import BaseEngine
from dict.pager import print_in_columns

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
)


@dataclass
class SynonimResult:
    """A result from the synonim.net engine."""

    meaning: str
    synonyms: list[str]


class SynonimEngine(BaseEngine[SynonimResult]):
    """synonim.net engine."""

    names = ["synonim"]

    def __init__(self) -> None:
        """Initialize self."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
            }
        )
        super().__init__()

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[SynonimResult]:
        url = f"https://synonim.net/synonim/{urllib.parse.quote(phrase)}"

        response = self.session.get(url)
        if response.status_code == 404:
            return
        response.raise_for_status()
        content = response.text

        doc = lxml.html.fromstring(content)

        yield SynonimResult(
            meaning="wszystkie wyrazy",
            synonyms=[node.text for node in doc.cssselect("#mall a")],
        )

        for group in doc.cssselect("#mgru span"):
            yield SynonimResult(
                meaning=group.cssselect("h3 a")[0].text,
                synonyms=[node.text for node in group.cssselect("ul li a")],
            )

    def print_results(
        self, results: Iterable[SynonimResult], file: IO[str]
    ) -> None:
        for result in results:
            print(f"{COLOR_HIGHLIGHT}{result.meaning}{COLOR_RESET}", file=file)
            print_in_columns(result.synonyms, file=file)
