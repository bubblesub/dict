"""Main executable routine."""
import argparse
import io
import readline  # pylint: disable=unused-import
import sys
from typing import Optional

from dict.colors import COLOR_ERROR, COLOR_PROMPT, COLOR_RESET
from dict.engines import BaseEngine
from dict.pager import pager


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments.

    :return: parsed command line arguments
    """
    root_parser = argparse.ArgumentParser(
        prog="dict",
        description="Looks up phrases in a chosen dictionary",
        add_help=False,
    )
    root_parser.add_argument(
        "-e",
        "--engine",
        choices=sum([cls.names for cls in BaseEngine.__subclasses__()], []),
        help="engine to use",
    )
    root_parser.add_argument(
        "-N",
        "--no-pager",
        action="store_false",
        dest="use_pager",
        help="disable pager in interactive mode",
    )
    root_parser.add_argument("phrase", nargs="?")

    # first round: parse common options, do not interpret --help
    ret, remaining_args = root_parser.parse_known_args(args)

    # try to get the engine
    engine: Optional[BaseEngine] = None
    for cls in BaseEngine.__subclasses__():
        if ret.engine in cls.names:
            engine = cls()
            break

    # construct a child parser, add engine-specific options if applicable
    main_parser = argparse.ArgumentParser(
        prog=root_parser.prog,
        description=root_parser.description,
        parents=[root_parser],
    )
    if engine:
        engine.decorate_arg_parser(main_parser)

    # second round: parse everything, including --help, which raises SystemExit
    ret = main_parser.parse_args(args + remaining_args)

    # if --help was given, interpreting it raised SystemExit above, so at this
    # point --engine is required to carry out with the normal program operation
    if not ret.engine:
        main_parser.error("the following arguments are required: -e/--engine")

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
                parsed_args.engine.print_results(results=results, file=file)
            else:
                print(COLOR_ERROR + "no results" + COLOR_RESET, file=file)

            if parsed_args.use_pager:
                pager(file.getvalue().rstrip() + "\n")
            else:
                print(file.getvalue().rstrip())

    if parsed_args.phrase is not None:
        # one-shot
        work(parsed_args.phrase)
    else:
        # interactive prompt
        while True:
            try:
                phrase = input(
                    f"{COLOR_PROMPT}"
                    f"{parsed_args.engine.primary_name}>"
                    f"{COLOR_RESET} "
                )
            except (EOFError, KeyboardInterrupt):
                break

            work(phrase)


if __name__ == "__main__":
    main(sys.argv[1:])
