"""Definition of SJPEngine."""
import argparse
import re
import urllib.parse
from collections.abc import Iterable
from dataclasses import dataclass
from typing import IO

import lxml.html
import requests

from dict.colors import COLOR_HIGHLIGHT, COLOR_RESET
from dict.engines.base import BaseEngine


@dataclass
class SJPResult:
    """A result from the Słownik Języka Polskiego engine."""

    term: str
    definitions: list[str]


def _collect_text(node):
    doc = lxml.html.document_fromstring(lxml.html.tostring(node))
    for br_node in doc.xpath("*//br"):
        br_node.tail = "\n" + br_node.tail if br_node.tail else "\n"
    return doc.text_content()


class SJPEngine(BaseEngine[SJPResult]):
    """Słownik Języka Polskiego engine."""

    name = "sjp"

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[SJPResult]:
        url = f"http://sjp.pl/{urllib.parse.quote(phrase)}"
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        doc = lxml.html.fromstring(content)
        for header in doc.cssselect("h1"):
            term = header.text
            definitions = []
            for node in header.itersiblings():
                if re.search(
                    "medium.*sans-serif", node.attrib.get("style", "")
                ):
                    text = _collect_text(node).strip()
                    text = re.sub(r"\n\s+", "\n", text)
                    definitions.append(text)
                if node.tag == "hr" or node.tag == "h1":
                    break
            yield SJPResult(term=term, definitions=definitions)

    def print_results(
        self, results: Iterable[SJPResult], file: IO[str]
    ) -> None:
        for result in results:
            print(COLOR_HIGHLIGHT + result.term + COLOR_RESET, file=file)
            for definition in result.definitions:
                print(definition, file=file)
            print(file=file)
