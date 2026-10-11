"""Test doubles for code that depends on llmkit protocols.

Shipped inside the library on purpose: any project that uses llmkit can import
``FakeCompleter`` to test its own LLM code without network calls or API costs.
"""

from __future__ import annotations


class FakeCompleter:
    """A stand-in LLM that satisfies :class:`llmkit.Completer`.

    Records every prompt it receives and returns a canned reply.

    Args:
        reply: The text returned by every call to :meth:`complete`.

    Examples:
        >>> fake = FakeCompleter(reply="hi")
        >>> fake.complete("hello")
        'hi'
        >>> fake.prompts
        ['hello']
    """

    def __init__(self, reply: str = "  a short summary  ") -> None:
        self.reply = reply
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        """Record ``prompt`` and return the canned reply."""
        self.prompts.append(prompt)
        return self.reply
