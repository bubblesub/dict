"""Utilities related to terminal output."""
import io
import shutil
import subprocess
from collections.abc import Iterable
from typing import IO


def pager(text: str) -> None:
    """Page through text in the terminal by feeding it to another program."""
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        "less -C -r", shell=True, stdin=subprocess.PIPE
    )

    if proc.stdin:
        try:
            with io.TextIOWrapper(
                proc.stdin, errors="backslashreplace"
            ) as pipe:
                try:
                    pipe.write(text)
                except KeyboardInterrupt:
                    # We've hereby abandoned whatever text hasn't been written,
                    # but the pager is still in control of the terminal.
                    pass
        except OSError:
            pass  # Ignore broken pipes caused by quitting the pager program.

    while True:
        try:
            proc.wait()
            break
        except KeyboardInterrupt:
            # Ignore ctl-c like the pager itself does.  Otherwise the pager is
            # left running and the terminal is in raw mode and unusable.
            pass


def print_in_columns(
    items: Iterable[str], file: IO[str], column_size: int = 0
) -> None:
    """Print items in columns, filling the terminal horizontally.

    :param items: list of phrases to print in columns
    :param file: output stream
    :param column_size: max item length, if empty, calculate automatically
    """
    items = [f"- {item} " for item in items]
    if not column_size:
        column_size = max((len(item) for item in items), default=5)
    term_size = shutil.get_terminal_size()
    columns = term_size.columns // column_size
    while items:
        row = ""
        for _ in range(columns):
            if not items:
                break
            item = items.pop(0)
            row += f"{item:<{column_size}s}"
        row = row.rstrip()
        print(row, end="\n" if len(row) < term_size.columns else "", file=file)
    print(file=file)
