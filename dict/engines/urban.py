"""Definition of the UrbanEngine."""
import argparse
from collections.abc import Iterable
from dataclasses import dataclass
from typing import IO

import requests

from dict.engines.base import BaseEngine
from dict.text import wrap_long_text

DEFAULT_MAX_DEFINITIONS = 3


@dataclass
class UrbanResult:
    """A result from the Urban Dictionary engine."""

    definition: str
    example: str
    thumbs_up: int
    thumbs_down: int


class UrbanEngine(BaseEngine[UrbanResult]):
    """Urban Dictionary engine."""

    names = ["urban"]

    @staticmethod
    def decorate_arg_parser(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-n",
            "--num",
            type=int,
            help="How many definitions to print.",
            default=DEFAULT_MAX_DEFINITIONS,
        )

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[UrbanResult]:
        url = "http://api.urbandictionary.com/v0/define"
        response = requests.get(url, {"term": phrase})
        response.raise_for_status()
        content = response.json()

        for entry in list(
            sorted(content["list"], key=lambda item: -item["thumbs_up"])
        )[0 : args.num]:
            yield UrbanResult(
                definition=entry["definition"],
                example=entry["example"],
                thumbs_up=entry["thumbs_up"],
                thumbs_down=entry["thumbs_down"],
            )

    def print_results(
        self, results: Iterable[UrbanResult], file: IO[str]
    ) -> None:
        for result in results:
            print("Definition:", file=file)
            print(wrap_long_text(result.definition), file=file)
            print(file=file)
            print("Example:", file=file)
            print(wrap_long_text(result.example), file=file)
            print(
                "+%d -%d" % (result.thumbs_up, result.thumbs_down), file=file
            )
            print(file=file)
            print("-" * 50, file=file)
            print(file=file)
