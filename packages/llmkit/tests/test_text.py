"""Tests for llmkit.text module."""

import pytest

from llmkit.text import chunk_text, normalize_whitespace, truncate, word_count


## --- word_count() tests ---
def test_word_count_basic() -> None:
    assert word_count("hello world") == 2


def test_word_count_empty() -> None:
    assert word_count("") == 0


def test_word_count_extra_whitespace() -> None:
    assert word_count("  a   b  ") == 2


## --- truncate() tests ---
def test_truncate_no_change_when_short() -> None:
    assert truncate("short", 20) == "short"


def test_truncate_shortens_with_suffix() -> None:
    result = truncate("hello world", 8)  # Arrange + Act: set up input, call function
    assert result == "hello..."  # Assert: is it what we expect?
    assert len(result) <= 8  # a second assert to check another property


def test_truncate_raises_on_bad_max() -> None:
    with pytest.raises(ValueError):
        truncate("anything", 0)


def test_truncate_suffix_longer_than_max() -> (
    None
):  # when max_chars is smaller than the suffix, return a clipped suffix
    assert truncate("hello", 2) == ".."


## --- normalize_whitespace() tests ---
def test_normalize_collapses_and_strips() -> None:  # happy path. general case.
    assert normalize_whitespace("a\n\n b\t\tc ") == "a b c"


def test_normalize_empty() -> None:  # edge case: empty string
    assert normalize_whitespace("") == ""


def test_normalize_only_whitespace() -> None:  # edge case: nothing but whitespace
    assert normalize_whitespace("   \t\n  ") == ""


## --- chunk_text() tests ---
def test_chunk_no_overlap() -> None:  # happy path, general case, with default overlap=0
    assert chunk_text("abcdefghij", 4) == ["abcd", "efgh", "ij"]


def test_chunk_with_overlap() -> None:  # happy path, general case, with overlap=2
    assert chunk_text("abcdefghij", 4, overlap=2) == ["abcd", "cdef", "efgh", "ghij", "ij"]


def test_chunk_exact_fit() -> None:  # edge case: text length equals chunk size
    assert chunk_text("abcd", 4) == ["abcd"]


def test_chunk_empty() -> None:  # edge case: empty input string
    assert chunk_text("", 4) == []


def test_chunk_raises_on_bad_size() -> None:  # edge case: size <= overlap int. testing error bucket
    with pytest.raises(ValueError):
        chunk_text("abc", 0)


def test_chunk_raises_when_overlap_too_big() -> (
    None
):  # edge case: overlap == size. testing error bucket
    with pytest.raises(ValueError):
        chunk_text("abc", 4, overlap=4)


def test_chunk_raises_on_negative_overlap() -> None:  # edge case: overlap < 0. testing error bucket
    with pytest.raises(ValueError):
        chunk_text("abc", 4, overlap=-1)
