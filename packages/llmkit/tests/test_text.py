"""Tests for llmkit.text module."""
import pytest

from llmkit.text import truncate, word_count

def test_word_count_basic():
    assert word_count("hello world") == 2


def test_word_count_empty():
    assert word_count("") == 0

def test_word_count_extra_whitespace():
    assert word_count("  a   b  ") == 2

def test_truncate_no_change_when_short():
    assert truncate("short", 20) == "short"

def test_truncate_shortens_with_suffix():
    result = truncate("hello world", 8)
    assert result == "hello..."
    assert len(result) <= 8 

def test_truncate_raises_on_bad_max():
    with pytest.raises(ValueError):
        truncate("anything", 0) 


