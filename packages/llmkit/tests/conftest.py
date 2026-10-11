"""Shared pytest fixtures. pytest loads this file automatically; no import needed."""

import pytest

from llmkit.testing import FakeCompleter


@pytest.fixture
def fake() -> FakeCompleter:
    """A fresh FakeCompleter for each test that asks for one."""
    return FakeCompleter()
