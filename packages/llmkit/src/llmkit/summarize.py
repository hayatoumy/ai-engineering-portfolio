"""Summarization helpers built on the Completer protocol."""

from __future__ import annotations

from llmkit.protocols import Completer

_TEMPLATE = (
    "Summarize the text below in at most {max_words} words. "
    "Return only the summary, with no preamble.\n\n"
    "<text>\n{text}\n</text>"
)


def build_summary_prompt(text: str, max_words: int = 50) -> str:
    """Render the summarization prompt.

    Kept separate from :func:`summarize` so it can be tested without any client and
    so prompt changes are visible in diffs. This separation pays off on Day 09 when
    prompts get versioned.

    Args:
        text: Text to summarize.
        max_words: Upper bound to request from the model.

    Returns:
        The rendered prompt string.

    Raises:
        ValueError: If ``max_words`` is not positive or ``text`` is blank.
    """
    if max_words <= 0:
        raise ValueError(f"max_words must be positive, got {max_words}")
    if not text.strip():
        raise ValueError("text must not be blank")
    return _TEMPLATE.format(max_words=max_words, text=text)


def summarize(client: Completer, text: str, max_words: int = 50) -> str:
    """Summarize ``text`` using any object satisfying :class:`Completer`.

    Args:
        client: Any object with a ``complete(prompt: str) -> str`` method.
        text: Text to summarize.
        max_words: Upper bound to request from the model.

    Returns:
        The model's summary, stripped of surrounding whitespace.
    """
    return client.complete(build_summary_prompt(text, max_words)).strip()
