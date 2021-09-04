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


def expand_sgml(text: str) -> str:
    """Replaces &#...; SGML entities to their Unicode character equivalents.

    :param text: HTML to transform
    :return: transformed text
    """
    return re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)


def strip_html(text: str) -> str:
    """Strip HTML tags from the input text.

    :param text: HTML to sanitize
    :return: sanitized text
    """
    return re.sub("<[^>]*>", "", text)
