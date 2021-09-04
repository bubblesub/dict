"""Definition of the ReversoEngine."""
import argparse
import urllib.parse
from collections.abc import Iterable
from dataclasses import dataclass
from typing import IO

import lxml.etree
import requests

from dict.colors import COLOR_HIGHLIGHT, COLOR_RESET
from dict.engines.base import BaseEngine
from dict.text import expand_sgml, strip_html

BASE_URL = "http://context.reverso.net/translation"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
)
LANG_MAP = {
    "ar": "arabic",
    "de": "german",
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "he": "hebrew",
    "it": "italian",
    "ja": "japanese",
    "nl": "dutch",
    "pl": "polish",
    "pt": "portuguese",
    "ro": "romanian",
    "ru": "russian",
}


@dataclass
class ReversoResult:
    """A result from the reverso.net engine."""

    source: str
    target: str


def _format_html(node: lxml.etree.Element) -> str:
    html = lxml.etree.tostring(node, encoding="unicode")
    html = html.replace("<em>", COLOR_HIGHLIGHT).replace("</em>", COLOR_RESET)
    html = expand_sgml(html)
    html = strip_html(html)
    html = html.strip()
    return html


class ReversoEngine(BaseEngine[ReversoResult]):
    """Reverso.net engine."""

    name = "reverso"

    @staticmethod
    def decorate_arg_parser(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-n", "--no-conjugations", action="store_false", dest="conjugate"
        )
        parser.add_argument(
            "-s",
            "--source-lang",
            metavar="src-lang",
            default="en",
            dest="src_lang",
            choices=LANG_MAP.keys(),
        )
        parser.add_argument(
            "-d",
            "--dest-lang",
            metavar="dst-lang",
            default="pl",
            dest="dst_lang",
            choices=LANG_MAP.keys(),
        )

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[ReversoResult]:
        src_language = LANG_MAP[args.src_lang]
        dst_language = LANG_MAP[args.dst_lang]
        conjugate: bool = args.conjugate

        url = (
            f"{BASE_URL}/{src_language}-{dst_language}/"
            f"{urllib.parse.quote(phrase)}?d={conjugate:d}"
        )

        response = requests.get(
            url, {"d": int(conjugate)}, headers={"User-Agent": USER_AGENT}
        )
        if response.status_code == 404:
            return
        response.raise_for_status()
        content = response.text

        doc = lxml.etree.HTML(content)
        for example_node in doc.cssselect("div.example"):
            src_node = example_node.cssselect("div.src span.text")[0]
            dst_node = example_node.cssselect("div.trg span.text")[0]
            yield ReversoResult(
                source=_format_html(src_node),
                target=_format_html(dst_node),
            )

    def print_results(
        self, results: Iterable[ReversoResult], file: IO[str]
    ) -> None:
        for result in results:
            print(result.source, file=file)
            print(result.target, file=file)
            print(file=file)
