# pylint: disable=invalid-name
"""Wildcard handlers."""

from difflib import SequenceMatcher
from pathlib import Path
import typing as t


def find_wildcards(string: str) -> t.Iterator[int]:
    """Find '%'s in string."""
    i = len(string)
    while i >= 0:
        j = string.rfind("%", 0, i)
        if j < 0:
            break
        if j == 0 or string[j - 1] != "%":
            yield j
        i = j


def replace_wildcards(string: str, replacement: str) -> str:
    """Replace '%'s in string."""
    for i in find_wildcards(string):
        string = f"{string[:i]}{replacement}{string[i+1:]}"
    return string


def has_wildcard(string: str) -> bool:
    """Check if string has '%'s."""
    try:
        next(find_wildcards(string))
        return True
    except StopIteration:
        return False


def get_non_matching_blocks(a: str, b: str) -> t.Iterable[t.Tuple[str, str]]:
    """Generates non-matching pairs."""
    sm = SequenceMatcher(None, a, b)
    matching = sm.get_matching_blocks()

    assert len(matching) >= 2
    head = matching[0]
    if head.a > 0 or head.b > 0:
        da = a[:head.a]
        db = b[:head.b]
        if da or db:
            yield da, db

    for i in range(1, len(matching)):
        current = matching[i]
        prev = matching[i - 1]
        da = a[prev.a + prev.size:current.a]
        db = b[prev.b + prev.size:current.b]
        if da or db:
            yield da, db


def get_wildcard_candidates(root: Path, pattern: str) -> t.Iterable[str]:
    """Generate substrings that satisfy wildcard pattern."""
    src = root/"src"
    for path in src.glob(pattern):
        xs, ys = (
            tuple(
                zip(
                    *get_non_matching_blocks(
                        pattern,
                        str(path.relative_to(src)),
                    )
                )
            )
            or ((), ())
        )
        if xs == ("*",) and len(ys) == 1:
            yield ys[0]
