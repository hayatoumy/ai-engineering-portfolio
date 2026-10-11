"""Tests for llmkit.summarize, using a fake LLM so no test touches the network."""

import pytest

from llmkit import Completer
from llmkit.summarize import build_summary_prompt, summarize
from llmkit.testing import FakeCompleter


## --- the fake itself ---
def test_fake_satisfies_completer_protocol(fake: FakeCompleter) -> None:
    assert isinstance(fake, Completer)


## --- build_summary_prompt() tests ---
def test_prompt_includes_text_and_limit() -> None:
    prompt = build_summary_prompt("The cat sat.", max_words=10)
    assert "The cat sat." in prompt
    assert "at most 10 words" in prompt


def test_prompt_rejects_non_positive_max_words() -> None:
    with pytest.raises(ValueError, match="max_words must be positive"):
        build_summary_prompt("some text", max_words=0)


def test_prompt_rejects_blank_text() -> None:
    with pytest.raises(ValueError, match="text must not be blank"):
        build_summary_prompt("   \n  ")


## --- summarize() tests ---
def test_summarize_strips_model_reply(fake: FakeCompleter) -> None:
    assert summarize(fake, "Some long text.") == "a short summary"


def test_summarize_sends_exactly_one_rendered_prompt(fake: FakeCompleter) -> None:
    summarize(fake, "Some long text.", max_words=5)
    assert fake.prompts == [build_summary_prompt("Some long text.", max_words=5)]
