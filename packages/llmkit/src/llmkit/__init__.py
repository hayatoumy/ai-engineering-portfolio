"""llmkit - small, well-tested utilities for building LLM applications."""

__version__ = "0.1.0"

from llmkit.protocols import Completer
from llmkit.summarize import build_summary_prompt, summarize
from llmkit.text import chunk_text, normalize_whitespace, truncate, word_count

__all__ = [
    "Completer",
    "__version__",
    "build_summary_prompt",
    "chunk_text",
    "normalize_whitespace",
    "summarize",
    "truncate",
    "word_count",
]
