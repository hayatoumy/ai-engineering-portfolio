"""Tests for llmkit.text module."""

import pytest

from llmkit.text import chunk_text, normalize_whitespace, truncate, word_count


## --- word_count() tests ---
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("hello world", 2),  # happy path
        ("", 0),  # empty input
        ("one", 1),  # single word
        ("  a   b  ", 2),  # extra spaces
        ("a\nb\tc", 3),  # newlines and tabs also separate words
    ],
)
def test_word_count(text: str, expected: int) -> None:
    assert word_count(text) == expected


## --- truncate() tests ---
@pytest.mark.parametrize(
    ("text", "max_chars", "expected"),
    [
        ("short", 20, "short"),  # under the limit: unchanged
        ("hello", 5, "hello"),  # exactly at the limit: unchanged
        ("hello!", 5, "he..."),  # one past the limit: truncated
        ("hello world", 8, "hello..."),  # happy path
        ("hello", 2, ".."),  # limit shorter than the suffix: clipped suffix
    ],
)
def test_truncate(text: str, max_chars: int, expected: str) -> None:
    result = truncate(text, max_chars)
    assert result == expected
    assert len(result) <= max_chars  # the promise in the docstring


def test_truncate_custom_suffix() -> None:
    assert truncate("hello world", 7, suffix="~") == "hello ~"


@pytest.mark.parametrize("max_chars", [0, -1])
def test_truncate_rejects_non_positive_max_chars(max_chars: int) -> None:
    with pytest.raises(ValueError, match="max_chars must be positive"):
        truncate("anything", max_chars)


## --- normalize_whitespace() tests ---
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a\n\n b\t\tc ", "a b c"),  # happy path: collapse and strip
        ("already clean", "already clean"),  # nothing to do
        ("", ""),  # empty input
        ("   \t\n  ", ""),  # only whitespace
    ],
)
def test_normalize_whitespace(text: str, expected: str) -> None:
    assert normalize_whitespace(text) == expected


## --- chunk_text() tests ---
@pytest.mark.parametrize(
    ("text", "size", "overlap", "expected"),
    [
        ("abcdefghij", 4, 0, ["abcd", "efgh", "ij"]),  # happy path, no overlap
        ("abcdefghij", 4, 2, ["abcd", "cdef", "efgh", "ghij", "ij"]),  # with overlap
        ("abcd", 4, 0, ["abcd"]),  # exact fit
        ("abc", 10, 0, ["abc"]),  # text shorter than one chunk
        ("abc", 1, 0, ["a", "b", "c"]),  # smallest legal size
        ("", 4, 0, []),  # empty input
    ],
)
def test_chunk_text(text: str, size: int, overlap: int, expected: list[str]) -> None:
    assert chunk_text(text, size, overlap) == expected


@pytest.mark.parametrize(
    ("size", "overlap", "message"),
    [
        (0, 0, "size must be positive"),
        (-1, 0, "size must be positive"),
        (4, -1, "overlap must be non-negative"),
        (4, 4, "must be less than the size"),  # overlap == size
        (4, 5, "must be less than the size"),  # overlap > size
    ],
)
def test_chunk_text_rejects_bad_arguments(size: int, overlap: int, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        chunk_text("abc", size, overlap)
