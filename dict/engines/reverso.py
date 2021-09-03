"""Definition of the ReversoEngine."""
import argparse
import re
import urllib.parse
import urllib.request
from collections.abc import Iterable

import lxml.etree

from dict.colors import COLOR_HIGHLIGHT, COLOR_RESET
from dict.engines.base import BaseEngine

BASE_URL = "http://context.reverso.net/translation/"
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


def _format_html(node: lxml.etree.Element) -> str:
    html = lxml.etree.tostring(node, encoding="unicode")
    html = html.replace("<em>", COLOR_HIGHLIGHT).replace("</em>", COLOR_RESET)
    html = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), html)
    html = re.sub("<[^>]*>", "", html)
    html = html.strip()
    return html


class ReversoEngine(BaseEngine):
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
        parser.add_argument(
            "-N",
            action="store_false",
            dest="use_pager",
            help="disable pager in interactive mode",
        )

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[str]:
        src_language = LANG_MAP[args.src_lang]
        dst_language = LANG_MAP[args.dst_lang]
        conjugate: bool = args.conjugate

        url = (
            BASE_URL
            + f"{src_language}-{dst_language}/"
            + f"{urllib.parse.quote(phrase)}"
            + f"?d={conjugate:d}"
        )

        request = urllib.request.Request(
            url=url, headers={"User-Agent": USER_AGENT}
        )

        try:
            with urllib.request.urlopen(request) as handle:
                content = handle.read()
                doc = lxml.etree.HTML(content)
                for example_node in doc.cssselect("div.example"):
                    src_node = example_node.cssselect("div.src span.text")[0]
                    dst_node = example_node.cssselect("div.trg span.text")[0]
                    yield "\n".join(
                        [
                            _format_html(src_node),
                            _format_html(dst_node),
                        ]
                    )
        except urllib.error.HTTPError as ex:
            if ex.code == 404:
                return
            raise
