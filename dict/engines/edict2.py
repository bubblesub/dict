"""Definition of the Edict2Engine."""
import argparse
import gzip
import re
from collections.abc import Iterable
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import IO, Optional

import xdg

from dict.colors import COLOR_HIGHLIGHT, COLOR_RESET
from dict.engines.base import BaseEngine
from dict.http import download

PART_OF_SPEECH_CODES = (
    "adj-i adj-na adj-no adj-pn adj-t adj-f adj adv adv-to aux aux-v aux-adj "
    "conj ctr exp int iv n n-adv n-suf n-pref n-t num pn pref prt suf v1 "
    "v2a-s v4h v4r v5 v5aru v5b v5g v5k v5k-s v5m v5n v5r v5r-i v5s v5t v5u "
    "v5u-s v5uru v5z vz vi vk vn vr vs vs-s vs-i vt"
).split()

FIELD_OF_APPLICATION_CODES = (
    "Buddh MA comp food geom ling math mil physics chem biol"
).split()

MISCELLANEOUS_CODES = (
    "X abbr arch ateji chn col derog eK ek fam fem gikun hon hum iK id ik io "
    "m-sl male male-sl oK obs obsc ok on-mim poet pol rare sens sl uK uk vulg "
    "P"
).split()

DIALECT_CODES = "kyb osb ksb ktb tsb thb tsug kyu rkb nab".split()

_RE_KANA = re.compile(r"\[(.+)\]")
_RE_FIELD_TAGS = re.compile(r"\{(%s)\}" % "|".join(FIELD_OF_APPLICATION_CODES))
_RE_NUMBER_TAG = re.compile(r"\((\d+)\)")
_RE_ANY_TAG = re.compile(r"\(([^)]*)\)")
_RE_RELATED_TAG = re.compile(r"\(See ([^)]*)\)", flags=re.IGNORECASE)
_RE_TAGS = re.compile(
    r"\(((?:%s|[,]+)+)\:?\)"
    % "|".join(PART_OF_SPEECH_CODES + MISCELLANEOUS_CODES + DIALECT_CODES)
)

DOWNLOAD_URL = "http://ftp.edrdg.org/pub/Nihongo/edict2.gz"
CACHE_PATH = Path(xdg.XDG_CACHE_HOME) / "edict2.txt"


@dataclass
class Edict2Japanese:
    """Japanese part of an edict2 result."""

    kanji: str
    kana: str
    kanji_tags: list[str]
    kana_tags: list[str]


@dataclass
class Edict2Glossary:
    """English part of an edict2 result."""

    english: str
    tags: list[str]
    field: Optional[str]
    related: list[str]


@dataclass
class Edict2Result:
    """A result from the edict2 engine."""

    glossaries: list[Edict2Glossary]
    japanese: list[Edict2Japanese]
    tags: list[str]
    ent_seq: Optional[str]
    has_audio: bool


def _extract_tags(
    word: str, expression: re.Pattern[str]
) -> tuple[str, list[str]]:
    tags: list[str] = []
    if match := expression.search(word):
        for group in match.groups():
            tags.extend(group.split(","))
        word = expression.sub("", word)
    return word, tags


def _extract_related(glossaries: str) -> tuple[str, list[str]]:
    return _extract_tags(word=glossaries, expression=_RE_RELATED_TAG)


def _extract_fields(glossaries: str) -> tuple[str, list[str]]:
    return _extract_tags(word=glossaries, expression=_RE_FIELD_TAGS)


def parse_edict2_line(raw_entry: str) -> Edict2Result:
    """Parse a line from the edict2.txt dictionary into a result object.

    :param raw_entry: input line
    :return: parsed entry
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    raw_words = raw_entry.split(" ")
    raw_kanji = raw_words[0].split(";")
    kana_match = _RE_KANA.match(raw_words[1])
    if kana_match:
        raw_kana = kana_match.group(1).split(";")
    else:
        raw_kana = raw_kanji

    kanji_tagged = [_extract_tags(k, _RE_TAGS) for k in raw_kanji]
    kana_tagged = [_extract_tags(k, _RE_TAGS) for k in raw_kana]

    raw_english = raw_entry.split("/")[1:-2]

    english_word, main_tags = _extract_tags(raw_english[0], _RE_TAGS)
    english = [english_word] + raw_english[1:]

    if english[-1] == "(P)":
        main_tags = sorted(set(main_tags) | {"P"})
        english = english[:-1]

    # join numbered entries
    joined_english: list[str] = []
    has_numbers = False
    for word in english:
        clean, number = _extract_tags(word, _RE_NUMBER_TAG)
        clean = clean.strip()
        if number:
            has_numbers = True
            joined_english.append(clean)
        elif has_numbers:
            joined_english[-1] += "/" + clean
        else:
            joined_english.append(clean)
    english = joined_english

    glossaries = []
    for gloss in english:
        clean_gloss, related_words = _extract_related(gloss)
        clean_gloss, tags = _extract_tags(clean_gloss, _RE_TAGS)
        clean_gloss, fields = _extract_fields(clean_gloss)

        if related_words:
            related_words = related_words[0].split(",")
        else:
            related_words = []

        field = fields[0] if fields else None
        clean_gloss = clean_gloss.strip()
        if clean_gloss:
            glossaries.append(
                Edict2Glossary(
                    english=clean_gloss,
                    tags=tags,
                    field=field,
                    related=related_words,
                )
            )

    ent_seq = raw_entry.split("/")[-2]

    # entL sequences that end in X have audio clips
    has_audio = ent_seq[-1] == "X"

    # throw away the entL and X part, keeping only the id
    ent_seq = ent_seq[4:]
    if has_audio:
        ent_seq = ent_seq[:-1]

    japanese: list[Edict2Japanese] = []
    for kana, ktag in kana_tagged:
        # special case for kana like this:
        # おくび(噯,噯気);あいき(噯気,噫気,噯木)
        kana, matching_kanji = _extract_tags(kana, _RE_ANY_TAG)
        if matching_kanji:
            matching_kanji = matching_kanji[0].split(",")

        for kanji, jtag in kanji_tagged:
            if not matching_kanji or kanji in matching_kanji:
                japanese.append(
                    Edict2Japanese(
                        kanji=kanji, kana=kana, kanji_tags=jtag, kana_tags=ktag
                    )
                )

    return Edict2Result(
        japanese=japanese,
        glossaries=glossaries,
        tags=main_tags,
        ent_seq=ent_seq,
        has_audio=has_audio,
    )


def download_edict2_if_needed() -> None:
    """Download the Edict dictionary file, if it does not exist yet."""
    if CACHE_PATH.exists():
        return

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BytesIO() as handle:
        download(
            DOWNLOAD_URL,
            description="downloading the dictionary",
            handle=handle,
        )
        CACHE_PATH.write_text(
            gzip.decompress(handle.getvalue()).decode("euc-jp")
        )


class Edict2Engine(BaseEngine[Edict2Result]):
    """Edict2 engine (a Japanese textfile dictionary).

    Downloads Edict EUC-JP gzipped file, where each entry is represented by a
    single physical line. The search process is divided into two steps: first
    the entry is scanned with the input phrase interpreted as a regex. The
    physical lines that match are then parsed into logic entries and further
    filtered, this time within specific fields.
    """

    names = ["edict", "edict2"]

    def lookup_phrase(
        self, args: argparse.Namespace, phrase: str
    ) -> Iterable[Edict2Result]:
        download_edict2_if_needed()

        pattern = re.compile(phrase, flags=re.I)

        with CACHE_PATH.open("r") as handle:
            for line in handle:
                if pattern.search(line):
                    result = parse_edict2_line(line)
                    if any(
                        pattern.search(jap.kana) or pattern.search(jap.kanji)
                        for jap in result.japanese
                    ) or any(
                        pattern.search(glossary.english)
                        for glossary in result.glossaries
                    ):
                        yield result

    def print_results(
        self, results: Iterable[Edict2Result], file: IO[str]
    ) -> None:
        for result in results:
            print("({})".format(",".join(result.tags)), file=file)
            for jap in result.japanese:
                print(
                    f"{COLOR_HIGHLIGHT}{jap.kanji} ({jap.kana}){COLOR_RESET}",
                    file=file,
                )
            for glossary in result.glossaries:
                print(glossary.english, file=file)
            print(file=file)
