"""Pager() function declaration."""
import io
import subprocess


def pager(text: str) -> None:
    """Page through text in the terminal by feeding it to another program."""
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        "less -r", shell=True, stdin=subprocess.PIPE
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
