"""Text utilities."""
import re


def wrap_long_text(text: str, length: int = 70) -> str:
    """Word-wrap plain text to maximum of length columns.

    :param text: text to wrap
    :param length: maximum columns
    :return: wrapped text
    """
    return "\n".join(
        line.strip() for line in re.findall(r".{1,%d}(?:\s+|$)" % length, text)
    )
