"""Definition of the BaseEngine."""
import argparse
from collections.abc import Iterable


class BaseEngine:
    """Base dictionary engine."""

    name: str = NotImplemented

    @staticmethod
    def decorate_arg_parser(parser: argparse.ArgumentParser) -> None:
        """Add optional new arguments to the main argument parser.

        :param parser: parser to configure
        """
        raise NotImplementedError("not implemented")  # pragma: no cover

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[str]:
        """Look up the given phrase in the given dictionary.

        :param args: parsed command line arguments
        :param phrase: phrase to look up
        :return: a generator of string results to show
        """
        raise NotImplementedError("not implemented")  # pragma: no cover
