"""Tests for the dict.__main__ module."""
import argparse
import io
from collections.abc import Iterable
from typing import IO
from unittest.mock import patch

import pytest

from dict.__main__ import main, parse_args
from dict.engines import BaseEngine


class DummyEngine(BaseEngine[str]):
    """A dummy dictionary engine."""

    names = ["dummy-engine"]

    @staticmethod
    def decorate_arg_parser(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-p", "--pass", action="store_true", required=True)
        parser.add_argument("-t", "--test", action="store_true")

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[str]:
        if phrase:
            yield "".join(reversed(phrase))

    def print_results(self, results: Iterable[str], file: IO[str]) -> None:
        for result in results:
            print(result, file=file)


def test_parse_args_required_arg_missing() -> None:
    """Test decorating parse_args – optional argument missing."""
    with pytest.raises(SystemExit):
        parse_args(["-e", "dummy-engine"])


def test_parse_args_optional_arg_missing() -> None:
    """Test decorating parse_args – optional argument missing."""
    args = parse_args(["-e", "dummy-engine", "-p"])
    assert isinstance(args.engine, DummyEngine)
    assert args.test is False


def test_parse_args_optional_args_provided() -> None:
    """Test decorating parse_args – optional argument provided."""
    args = parse_args(["-e", "dummy-engine", "-p", "--test"])
    assert isinstance(args.engine, DummyEngine)
    assert args.test is True


def test_main_without_pager(capsys) -> None:
    """Test the main routine without the pager."""
    main(["-e", "dummy-engine", "--no-pager", "-p", "test"])
    assert capsys.readouterr().out == "tset\n"


def test_main_with_pager() -> None:
    """Test the main routine with the pager."""
    with patch("dict.__main__.pager") as fake_pager:
        main(["-e", "dummy-engine", "-p", "test"])
        fake_pager.assert_called_once_with("tset\n")


def test_main_no_results(capsys) -> None:
    """Test the main routine without the pager."""
    main(["-e", "dummy-engine", "--no-pager", "-p", ""])
    assert "no results" in capsys.readouterr().out


def test_main_interactive_mode(monkeypatch, capsys) -> None:
    """Test the main routine in interactive mode."""
    monkeypatch.setattr("sys.stdin", io.StringIO("test\n"))
    main(["-e", "dummy-engine", "--no-pager", "-p"])
    assert "tset\n" in capsys.readouterr().out
