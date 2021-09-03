"""Main executable routine."""
import argparse
import io
import readline  # pylint: disable=unused-import
import sys

from dict.colors import COLOR_ERROR, COLOR_PROMPT, COLOR_RESET
from dict.engines import BaseEngine
from dict.pager import pager


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments.

    :return: parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Looks up phrases in a chosen dictionary"
    )
    parser.add_argument(
        "-e",
        "--engine",
        choices=[cls.name for cls in BaseEngine.__subclasses__()],
        required=True,
    )
    parser.add_argument(
        "-N",
        "--no-pager",
        action="store_false",
        dest="use_pager",
        help="disable pager in interactive mode",
    )
    parser.add_argument("phrase", nargs="?")
    ret, remaining_args = parser.parse_known_args(args)
    engine = next(
        cls() for cls in BaseEngine.__subclasses__() if cls.name == ret.engine
    )
    engine.decorate_arg_parser(parser)
    ret = parser.parse_args(args + remaining_args)
    ret.engine = engine
    return ret


def main(args: list[str]) -> None:
    """Main script routine."""
    parsed_args = parse_args(args)

    def work(phrase: str) -> None:
        """Look up the phrase and display it in the console."""
        results = list(parsed_args.engine.lookup_phrase(parsed_args, phrase))

        with io.StringIO() as file:
            if results:
                for result in results:
                    print(result, file=file)
                    print(file=file)
            else:
                print(COLOR_ERROR + "no results" + COLOR_RESET, file=file)

            if parsed_args.use_pager:
                pager(file.getvalue())
            else:
                print(file.getvalue(), end="")

    if parsed_args.phrase is not None:
        # one-shot
        work(parsed_args.phrase)
    else:
        # interactive prompt
        while True:
            try:
                phrase = input(
                    f"{COLOR_PROMPT}{parsed_args.engine.name}> {COLOR_RESET}"
                )
            except (EOFError, KeyboardInterrupt):
                break

            work(phrase)


if __name__ == "__main__":
    main(sys.argv[1:])
