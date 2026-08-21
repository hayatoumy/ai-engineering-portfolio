"""Structural types (protocols) that llmkit code depends on.

Protocols let us depend on *shape* rather than inheritance. A test double, an
Anthropic client, and an OpenAI client can all satisfy ``Completer`` without sharing
a base class - which is exactly what makes this code easy to test.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Completer(Protocol):
    """Anything that can turn a prompt into a text completion."""

    def complete(self, prompt: str) -> str:
        """Return a text completion for ``prompt``."""
        ...
