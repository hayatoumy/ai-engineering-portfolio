"""llmkit - small utilities for building LLM applications."""

__version__ = "0.1.0"

from llmkit.text import chunk_text, normalize_whitespace, truncate, word_count

__all__ = ["__version__", "chunk_text", "normalize_whitespace", "truncate", "word_count"]
